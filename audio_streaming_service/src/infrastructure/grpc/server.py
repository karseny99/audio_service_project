import grpc
import asyncio
from concurrent import futures
from typing import AsyncIterator
from dependency_injector.wiring import inject, Provide
from containers import Container
from datetime import datetime

from src.domain.stream.models import StreamSession, StreamStatus
from src.core.protos.generated import streaming_pb2, streaming_pb2_grpc

from src.infrastructure.storage.audio_streamer import S3AudioStreamer

# Кастомные исключения для управления потоком
class StreamRestartException(Exception):
    """Требует перезапуска генератора чанков"""
    pass

class StreamPausedException(Exception):
    """Сессия поставлена на паузу"""
    pass

# @dataclass
# class StreamSession:
#     id: str
#     user_id: str
#     track_id: str
#     current_bitrate: str
#     position: int = 0
#     paused: bool = False
#     should_restart: bool = False

class AudioStreamingService(streaming_pb2_grpc.StreamingServiceServicer):
    def __init__(self, minio_client):
        self.minio_client = minio_client
        self.sessions: dict[str, StreamSession] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)

    async def StreamAudio(self, request_iterator: AsyncIterator[streaming_pb2.ClientMessage], context):
        try:
            # 1. Получаем начальный запрос
            start_request = await self._get_start_request(request_iterator)
            
            # 2. Инициализируем сессию
            session = await self._init_session(start_request)
            yield self._create_session_info(session)
            
            # 3. Запускаем задачу для чтения сообщений
            message_task = asyncio.create_task(
                self._read_client_messages(request_iterator, session)
            )
            
            # 4. Основной цикл обработки
            while session.status != StreamStatus.FINISHED:
                try:
                    async for chunk in self._generate_chunks(session):
                        yield streaming_pb2.ServerMessage(chunk=chunk)
                        
                        # Проверяем команды управления после каждого чанка
                        control_action = await self._check_control_messages(session)
                        if control_action:
                            await self._process_control(session, control_action)
                            
                except StreamRestartException:
                    continue
                except StreamPausedException:
                    await self._handle_pause(session)
                    
        except asyncio.CancelledError:
            session.status = StreamStatus.FINISHED
        finally:
            await self._cleanup_session(session)
            message_task.cancel()

    async def _read_client_messages(self, request_iterator, session):
        """Читает сообщения от клиента и складывает в очередь"""
        async for request in request_iterator:
            if session.message_queue is not None:
                await session.message_queue.put(request)
            else:
                print("Message queue not initialized")

    async def _check_control_messages(self, session) -> Optional[streaming_pb2.StreamControl]:
        """Проверяет очередь на наличие управляющих команд"""
        try:
            if session.message_queue.empty():
                return None
                
            request = await asyncio.wait_for(
                session.message_queue.get(), 
                timeout=0.001  # Неблокирующая проверка
            )
            
            if request.HasField("control"):
                return request.control
            elif request.HasField("ack"):
                await self._handle_chunk_ack(session, request.ack)
                
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            print(f"Error processing control messages: {e}")
            
        return None

    async def _process_control(self, session, control):
        """Обрабатывает управляющую команду"""
        if control.action == streaming_pb2.StreamControl.PAUSE:
            session.status = StreamStatus.PAUSED
            session.paused_at = datetime.now()
            session.pause_event.clear()
            raise StreamPausedException()
            
        elif control.action == streaming_pb2.StreamControl.RESUME:
            session.status = StreamStatus.STARTED
            session.pause_event.set()
            
        elif control.action == streaming_pb2.StreamControl.CHANGE_BITRATE:
            if control.bitrate in session.track.available_bitrates:
                session.current_bitrate = control.bitrate
                session.status = StreamStatus.SHOULD_RESTART
                raise StreamRestartException()
                
        elif control.action == streaming_pb2.StreamControl.SEEK:
            if 0 <= control.chunk_num < session.track.total_chunks:
                session.current_chunk = control.chunk_num
                session.status = StreamStatus.SHOULD_RESTART
                raise StreamRestartException()
                
        elif control.action == streaming_pb2.StreamControl.STOP:
            session.status = StreamStatus.FINISHED
            session.finished_at = datetime.now()

    async def _handle_pause(self, session):
        """Ожидает возобновления сессии"""
        await session.pause_event.wait()
        if session.status == StreamStatus.PAUSED:
            session.status = StreamStatus.STARTED

    async def _generate_chunks(self, session) -> AsyncIterator[AudioChunk]:
        """Генератор чанков с учетом текущего состояния"""
        streamer = AudioStreamer(
            self.minio_client,
            bucket="audio-bucket",
            track_id=session.track.track_id,
            bitrate=session.current_bitrate,
            start_chunk=session.current_chunk
        )
        
        async for chunk in streamer.chunks():
            if session.status == StreamStatus.PAUSED:
                raise StreamPausedException()
            if session.status == StreamStatus.FINISHED:
                break
                
            session.current_chunk = chunk.number
            yield chunk
            
            if chunk.is_last:
                session.status = StreamStatus.FINISHED
                session.finished_at = datetime.now()

    async def _init_session(self, request) -> StreamSession:
        """Инициализирует новую сессию"""
        track = await self._get_track_metadata(request.track_id)
        
        session = StreamSession(
            session_id=request.session_id or self._generate_session_id(),
            user_id=request.user_id,
            track=track,
            current_bitrate=request.bitrate,
            status=StreamStatus.STARTED,
            current_chunk=0,
            started_at=datetime.now(),
            message_queue=asyncio.Queue(),
            pause_event=asyncio.Event()
        )
        session.pause_event.set()  # Изначально не на паузе
        
        self.sessions[session.session_id] = session
        return session

    async def _get_track_metadata(self, track_id) -> AudioTrack:
        """Получает метаданные трека из хранилища"""
        # Реализация зависит от вашего хранилища
        return AudioTrack(
            track_id=track_id,
            total_chunks=100,  # Примерное значение
            available_bitrates=["128kbps", "320kbps"],
            duration_ms=240000  # 4 минуты
        )

    async def _cleanup_session(self, session):
        """Очищает ресурсы сессии"""
        if session.session_id in self.sessions:
            del self.sessions[session.session_id]
        if hasattr(session, 'message_queue'):
            session.message_queue = None

    def _create_session_info(self, session):
        return streaming_pb2.ServerMessage(
            session=streaming_pb2.SessionInfo(
                session_id=session.session_id,
                current_bitrate=session.current_bitrate,
                total_chunks=session.track.total_chunks,
                available_bitrates=session.track.available_bitrates
            )
        )

    async def _handle_chunk_ack(self, session, ack):
        """Обрабатывает подтверждение получения чанков"""
        # Можно добавить логику контроля потока
        pass