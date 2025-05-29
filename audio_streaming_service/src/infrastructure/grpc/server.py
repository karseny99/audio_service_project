from grpc import StatusCode
from dependency_injector.wiring import inject, Provide
import grpc
import asyncio
from typing import AsyncIterator, Optional
from src.core.di import Container
from src.core.protos.generated import music_streaming_pb2_grpc, music_streaming_pb2
from src.core.exceptions import (
    TrackNotFoundError,
    InvalidBitrateError,
    StreamingSessionError
)
from src.core.config import settings
from src.core.logger import logger

class StreamingService(music_streaming_pb2_grpc.StreamingServiceServicer):
    @inject
    def __init__(
        self,
        start_stream_uc=Provide[Container.start_stream_use_case],
        stream_chunks_uc=Provide[Container.stream_chunks_use_case],
        session_manager=Provide[Container.session_manager],
        event_publisher=Provide[Container.event_publisher]
    ):
        self._start_stream_uc = start_stream_uc
        self._stream_chunks_uc = stream_chunks_uc
        self._session_manager = session_manager
        self._event_publisher = event_publisher
        self._active_generators = {}  # session_id: generator

    async def StreamAudio(
        self,
        request_iterator: AsyncIterator[music_streaming_pb2.StreamRequest],
        context: grpc.ServicerContext
    ) -> AsyncIterator[music_streaming_pb2.DataChunk]:
        session_id = None
        current_generator = None
        
        try:
            async for request in request_iterator:
                # Обработка команд
                if request.HasField("start"):
                    session_id = await self._handle_start(request.start, context)
                    if session_id:
                        current_generator = self._create_chunk_generator(session_id)

                elif request.HasField("seek") and session_id:
                    await self._handle_seek(request.seek, session_id)
                    current_generator = self._create_chunk_generator(session_id)

                elif request.HasField("pause") and session_id:
                    await self._session_manager.pause(session_id)

                elif request.HasField("resume") and session_id:
                    await self._session_manager.resume(session_id)

                elif request.HasField("ping") and session_id:
                    await self._event_publisher.publish_chunk_delivered(
                        session_id=session_id,
                        offset=request.ping.offset
                    )

                # Отправка чанков, если есть активный генератор
                if current_generator:
                    try:
                        chunk = await current_generator.__anext__()
                        yield self._create_chunk_response(chunk)
                    except StopAsyncIteration:
                        current_generator = None

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            raise
        finally:
            if session_id:
                await self._cleanup_session(session_id)

    async def _handle_start(self, request, context) -> Optional[str]:
        try:
            session_id = await self._start_stream_uc.execute(
                user_id=self._get_user_id(context),
                track_id=request.track_id,
                bitrate=request.bitrate
            )
            return session_id
        except TrackNotFoundError:
            await context.abort(StatusCode.NOT_FOUND, "Track not found")
        except InvalidBitrateError:
            await context.abort(StatusCode.INVALID_ARGUMENT, "Unsupported bitrate")
        except Exception as e:
            logger.error(f"Start stream error: {str(e)}")
            await context.abort(StatusCode.INTERNAL, "Internal server error")
        return None

    async def _handle_seek(self, request, session_id: str):
        try:
            await self._session_manager.seek(
                session_id=session_id,
                offset=request.offset
            )
        except StreamingSessionError as e:
            logger.error(f"Seek error: {str(e)}")
            raise

    def _create_chunk_generator(self, session_id: str):
        """Создает новый генератор чанков для сессии"""
        session = self._session_manager.get_session(session_id)
        return self._stream_chunks_uc.execute(
            track_id=session.track_id,
            bitrate=session.bitrate,
            offset=session.offset
        )

    def _create_chunk_response(self, chunk) -> music_streaming_pb2.DataChunk:
        """Конвертирует доменный объект Chunk в gRPC ответ"""
        return music_streaming_pb2.DataChunk(
            data=chunk.data,
            offset=chunk.offset,
            is_last=chunk.is_last
        )

    async def _cleanup_session(self, session_id: str):
        """Корректно завершает сессию"""
        if session_id in self._active_generators:
            del self._active_generators[session_id]
        await self._session_manager.end_session(session_id)

    def _get_user_id(self, context) -> str:
        """Извлекает user_id из метаданных gRPC"""
        for key, value in context.invocation_metadata():
            if key == "user_id":
                return value
        context.abort(StatusCode.UNAUTHENTICATED, "Missing user_id")
        return ""

async def serve_grpc():
    server = grpc.aio.server()
    music_streaming_pb2_grpc.add_MusicStreamerServicer_to_server(
        StreamingService(), server
    )
    server.add_insecure_port(settings.get_grpc_url())
    
    await server.start()
    logger.info(f"gRPC streaming server started on {settings.get_grpc_url()}")
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Shutting down streaming server...")
        await server.stop(5)
        logger.info("Streaming server shutdown complete")