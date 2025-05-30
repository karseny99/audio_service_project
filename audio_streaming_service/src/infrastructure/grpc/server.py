import grpc
from grpc import StatusCode
import asyncio
from concurrent import futures
from typing import AsyncIterator
from dependency_injector.wiring import inject, Provide
from src.core.di import Container
from datetime import datetime
import uuid

from src.applications.use_cases.get_session import GetSessionUseCase
from src.applications.use_cases.chunk_generator import GetChunkGeneratorUseCase
from src.applications.use_cases.ack_chunks import AcknowledgeChunksUseCase
from src.applications.use_cases.control_session import AcknowledgeChunksUseCase
from src.core.protos.generated import streaming_pb2, streaming_pb2_grpc
from src.domain.stream.models import StreamSession, StreamStatus
from src.core.exceptions import UnknownMessageReceived
from src.core.di import Container
from src.core.logger import logger


class _StreamRestartException(Exception):
    """Требует перезапуска генератора чанков"""
    pass

class StreamInitError(Exception):
    pass


class StreamingService(streaming_pb2_grpc.StreamingServiceServicer):
    @inject
    def __init__(
            self,
            get_session_use_case: GetSessionUseCase = Provide[Container.get_session_use_case],
            get_chunk_generator_use_case: GetChunkGeneratorUseCase = Provide[Container.get_chunk_generator_use_case],
            acknowledge_chunks_use_case: AcknowledgeChunksUseCase = Provide[Container.get_ack_chunks_use_case]
        ):
        self._get_session_use_case = get_session_use_case
        self._get_chunk_generator_use_case = get_chunk_generator_use_case 
        self._acknowledge_chunks_use_case = acknowledge_chunks_use_case

    async def StreamAudio(
            self, 
            request_iterator: AsyncIterator[streaming_pb2.ClientMessage], 
            context: grpc.aio.ServicerContext
        ):
        session = None
        try:
            session = await self._init_session(request_iterator)
            
            while session.is_active():
                try:
                    chunk_generator = self._get_chunk_generator_use_case.execute(
                        session=session
                    )
                    
                    async for chunk in chunk_generator:
                        # Обрабатываем все накопленные сообщения
                        await self._process_client_messages(session)
                        
                        # Проверяем статус после обработки сообщений
                        if not session.should_continue():
                            if session.status == StreamStatus.PAUSED:
                                await self._wait_for_resume(session)
                            break
                             
                        # Отправляем чанк и обновляем состояние
                        yield self._create_chunk_message(chunk)
                        session.current_chunk = chunk.number + 1
                        
                        if chunk.is_last:
                            session.status = StreamStatus.FINISHED
                            session.finished_at = datetime.now()
                
                except _StreamRestartException:
                    continue  # Перезапускаем цикл с новыми параметрами
                    
        except Exception as e:
            # await self._handle_error(context, e)
            context.abort(StatusCode.INTERNAL, str(e))
        finally:
            if session:
                session.cleanup()


    async def _init_session(self, request_iterator) -> StreamSession:
        """Инициализирует сессию из первого сообщения клиента"""
        try:
            # Ждем начальное сообщение StartStream
            first_message = await anext(request_iterator)
            if not first_message.HasField("start"):
                raise ValueError("First message must be StartStream")
            
            start = first_message.start
            
            session_id = None
            if start.HasField("session_id"):
                session_id = start.session_id

            self._get_session_use_case._audio_streamer.initialize(
                track_id=start.track_id,
                initial_bitrate=start.bitrate,
            )

            session = await self._get_session_use_case.execute(
                track_id=start.track_id,
                user_id=start.user_id,
                bitrate=start.bitrate,
                session_id=session_id,
            )
            
            await session.message_queue.put(first_message)
            
            # Запускаем фоновую задачу чтения сообщений
            session.reader_task = asyncio.create_task(
                self._read_client_messages(request_iterator, session.message_queue)
            )
            
            return session
        
        except Exception as e:
            raise StreamInitError(f"Session initialization failed: {str(e)}")
    
    async def _read_client_messages(self, request_iterator, message_queue):
        """Читает сообщения от клиента и помещает в очередь сессии"""
        try:
            async for request in request_iterator:
                await message_queue.put(request)
        except Exception as e:
            logger.error(f"Error reading client messages: {str(e)}")
        finally:
            logger.info("Client message reader stopped")


    async def _wait_for_resume(self, session):
        """Ожидает возобновления сессии после паузы"""
        while session.status == StreamStatus.PAUSED and session.is_active():
            await self._process_client_messages(session)
            await asyncio.sleep(0.1)  # Небольшая задержка для CPU


    async def _process_client_messages(self, session):
        """Обрабатывает все сообщения в очереди"""
        while not session.message_queue.empty():
            request = await session.message_queue.get()
            if request.HasField("control"):
                await self._handle_control(request.control, session)
            elif request.HasField("ack"):
                await self._handle_ack(request.ack, session)
            else:
                raise UnknownMessageReceived(f"Received unknown msg: {request}")

    async def _handle_control(self, request: streaming_pb2.ClientMessage, session: StreamSession):
        try:
            if request.action == streaming_pb2.StreamControl.PAUSE:
                self._handle_pause(session)
                
            elif request.action == streaming_pb2.StreamControl.RESUME:
                self._handle_resume(session)
                
            elif request.action == streaming_pb2.StreamControl.STOP:
                self._handle_stop(session)
                
            elif request.action == streaming_pb2.StreamControl.CHANGE_BITRATE:
                await self._handle_change_bitrate(request, session)
                
            elif request.action == streaming_pb2.StreamControl.SEEK:
                self._handle_seek(request, session)
                
            else:
                raise UnknownMessageReceived(f"Unknown control action: {request}")
                
        except Exception as e:
            logger.error(f"Control action failed: {str(e)}")
            raise

    
    async def _handle_ack(self, request, session):
        self._acknowledge_chunks_use_case.execute(request.received_count, session)