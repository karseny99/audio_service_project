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
from src.applications.use_cases.save_session import SaveSessionUseCase
from src.applications.use_cases.chunk_generator import GetChunkGeneratorUseCase
from src.applications.use_cases.ack_chunks import AcknowledgeChunksUseCase
from src.applications.use_cases.control_session import (
    PauseSessionUseCase,
    ResumeSessionUseCase,
    StopSessionUseCase,
    ChangeSessionBitrateUseCase,
    ChangeSessionOffsetUseCase,
)
from src.core.protos.generated import streaming_pb2, streaming_pb2_grpc
from src.domain.stream.models import StreamSession, StreamStatus, AudioChunk
from src.core.exceptions import UnknownMessageReceived, AccessFail
from src.core.di import Container
from src.core.logger import logger
from src.core.config import settings


class _StreamRestartException(Exception):
    """Требует перезапуска генератора чанков"""
    pass

class _StreamCloseException(Exception):
    pass

class StreamInitError(Exception):
    pass


class StreamingService(streaming_pb2_grpc.StreamingServiceServicer):
    @inject
    def __init__(
            self,
            get_session_use_case:              GetSessionUseCase =              Provide[Container.get_session_use_case],
            get_chunk_generator_use_case:      GetChunkGeneratorUseCase =       Provide[Container.get_chunk_generator_use_case],
            acknowledge_chunks_use_case:       AcknowledgeChunksUseCase =       Provide[Container.get_ack_chunks_use_case],
            pause_session_use_case:            PauseSessionUseCase =            Provide[Container.get_pause_session_use_case],
            resume_session_use_case:           ResumeSessionUseCase =           Provide[Container.get_resume_session_use_case],
            stop_session_use_case:             StopSessionUseCase =             Provide[Container.get_stop_session_use_case],
            change_session_bitrate_use_case:   ChangeSessionBitrateUseCase =    Provide[Container.get_change_session_bitrate_use_case],
            change_session_offset_use_case:    ChangeSessionOffsetUseCase =     Provide[Container.get_change_session_offset_use_case],
            update_session_use_case:           SaveSessionUseCase =             Provide[Container.get_save_session_use_case]
        ):

        self._get_session_use_case = get_session_use_case
        self._get_chunk_generator_use_case = get_chunk_generator_use_case 
        self._acknowledge_chunks_use_case = acknowledge_chunks_use_case
        self._pause_session_use_case = pause_session_use_case
        self._resume_session_use_case = resume_session_use_case
        self._stop_session_use_case = stop_session_use_case
        self._change_session_bitrate_use_case = change_session_bitrate_use_case
        self._change_session_offset_use_case = change_session_offset_use_case
        self._update_session_use_case = update_session_use_case

    async def StreamAudio(
            self, 
            request_iterator: AsyncIterator[streaming_pb2.ClientMessage], 
            context: grpc.aio.ServicerContext
        ):
        session = None
        try:
            logger.info(f"Connection received{context}")
            session = await self._init_session(request_iterator)
            yield self._create_session_info_message(session)
            
            while session.is_active():
                try:
                    chunk_generator = self._get_chunk_generator_use_case.execute(
                        session=session
                    )
                    
                    async for chunk in chunk_generator:
                        # Обрабатываем все накопленные сообщения
                        if await self._is_connection_aborted(context):
                            logger.info(f"Connection aborted for session {session.session_id}")
                            return

                        await self._process_client_messages(session)
                        
                        # Проверяем статус после обработки сообщений
                        if not session.should_continue():
                            if session.status == StreamStatus.PAUSED:
                                await self._wait_for_resume(session, context)
                            break
                                
                        # Отправляем чанк и обновляем состояние
                        logger.debug(f"Chunks sent: {chunk.number}/{session.track.total_chunks - 1}, {chunk.number}")
                        yield self._create_chunk_message(chunk)

                        if session.should_stop():
                            session.stop()
                            break

                        session.current_chunk = chunk.number + 1
                        
                        if session.total_chunks_sent % 30 == 0:
                            await self._update_session_use_case.execute(session)

                        if chunk.is_last:
                            session.prestop()

                except _StreamRestartException:
                    yield self._create_session_info_message(session)
                    continue  # Перезапускаем цикл с новыми параметрами audio streamer

            logger.warn(f"Session {session.session_id} finished")
        except _StreamCloseException:
            logger.info(f"Stream for session {session.session_id} closed")
        except AccessFail as e:
            logger.error(f"No such file {str(e)}")
            await context.abort(StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            await context.abort(StatusCode.INTERNAL, str(e))
        finally:
            if session:
                await self._stop_session_use_case.execute(session)
                yield self._create_session_info_message(session)
                session.cleanup()

    async def _is_connection_aborted(self, context) -> bool:
        return False
        try:
            # Для grpc.aio
            return context.done() or await context.is_active() is False
        except Exception:
            return True

    async def _init_session(self, request_iterator) -> StreamSession:
        """Инициализирует сессию из первого сообщения клиента"""
        try:
            # Ждем начальное сообщение StartStream
            first_message = await anext(request_iterator)
            logger.info(f"Initializing session with {first_message}")
            if not first_message.HasField("start"):
                raise ValueError("First message must be StartStream")
            
            start = first_message.start
            session_id = None
            if start.HasField("session_id"):
                session_id = start.session_id

            await self._get_session_use_case._audio_streamer.initialize(
                track_id=start.track_id,
                initial_bitrate=start.bitrate,
            )

            session = await self._get_session_use_case.execute(
                track_id=start.track_id,
                user_id=start.user_id,
                bitrate=start.bitrate,
                session_id=session_id,
            )
            
            # Запускаем фоновую задачу чтения сообщений
            session.reader_task = asyncio.create_task(
                self._read_client_messages(request_iterator, session.message_queue)
            )
            
            return session
        
        except AccessFail:
            raise
        except Exception as e:
            raise StreamInitError(f"Session initialization failed: {str(e)}")
    
    def _create_chunk_message(self, chunk: AudioChunk) -> streaming_pb2.ServerMessage:
        return streaming_pb2.ServerMessage(
            chunk=streaming_pb2.AudioChunk(
                data=chunk.data,
                number=chunk.number,
                is_last=chunk.is_last,
                bitrate=chunk.bitrate,
            )
        )

    def _create_session_info_message(self, session: StreamSession) -> streaming_pb2.ServerMessage:
        logger.info(f"Notifying client about session changes")
        return streaming_pb2.ServerMessage(
            session=streaming_pb2.SessionInfo(
                session_id=session.session_id,
                current_bitrate=session.current_bitrate,
                available_bitrates=session.track.available_bitrates,
                current_chunk=session.current_chunk,
                total_chunks=session.track.total_chunks,
                chunk_size=session.chunk_size,
                status=self._convert_status_proto(session.status),
            )
        )

    def _convert_status_proto(self, status: StreamStatus):
        if status == StreamStatus.PAUSED:
            return streaming_pb2.SessionInfo.Status.PAUSED
        elif status == StreamStatus.STOPPED:
            return streaming_pb2.SessionInfo.Status.STOPPED
        else:
            return streaming_pb2.SessionInfo.Status.ACTIVE


    async def _read_client_messages(self, request_iterator, message_queue: asyncio.Queue):
        """Читает сообщения от клиента и помещает в очередь сессии"""
        try:
            async for request in request_iterator:
                logger.info(f"Received message: {request}")
                await message_queue.put(request)
        except Exception as e:
            logger.error(f"Error reading client messages: {str(e)}")
        finally:
            logger.info(f"Client message reader stopped {message_queue.qsize()}")


    async def _wait_for_resume(self, session: StreamSession, context):
        while session.status == StreamStatus.PAUSED and session.is_active():
            if await self._is_connection_aborted(context):
                return
                
            await asyncio.sleep(0.5)
            await self._process_client_messages(session)


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
                await self._pause_session_use_case.execute(session)
                
            elif request.action == streaming_pb2.StreamControl.RESUME:
                await self._resume_session_use_case.execute(session)
                
            elif request.action == streaming_pb2.StreamControl.STOP:
                # await self._stop_session_use_case.execute(session)
                raise _StreamCloseException("Control action: STOP stream")
                
            elif request.action == streaming_pb2.StreamControl.CHANGE_BITRATE:
                await self._change_session_bitrate_use_case.execute(request.bitrate, session)
                raise _StreamRestartException("Bitrate changed, chunk gen restart required")
            
            elif request.action == streaming_pb2.StreamControl.SEEK:
                await self._change_session_offset_use_case.execute(request.chunk_num, session)
                raise _StreamRestartException("Offset changed, chunk gen restart required")
            
            else:
                raise UnknownMessageReceived(f"Unknown control action: {request}")
        except _StreamCloseException:
            raise
        except _StreamRestartException:
            raise
        except Exception as e:
            logger.error(f"Control action failed: {str(e)}")
            raise

    
    async def _handle_ack(self, request, session):
        await self._acknowledge_chunks_use_case.execute(request.received_count, session)



async def serve_grpc():
    server = grpc.aio.server()
    streaming_pb2_grpc.add_StreamingServiceServicer_to_server(
        StreamingService(), server
    )
    server.add_insecure_port(settings.get_grpc_url())
    
    await server.start()
    logger.info(f"gRPC server started on {settings.get_grpc_url()}")
    
    try:
        while True:
            await asyncio.sleep(3600)  # Бесконечное ожидание
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Shutting down server...")
        await server.stop(5)
        logger.info("Server shutdown complete")