from src.core.config import settings
from src.core.logger import logger
from src.core.protos.generated import PlaylistCommands_pb2_grpc
from src.applications.use_cases.add_track import AddTrackToPlaylistUseCase
from src.applications.use_cases.add_playlist import AddPlaylistUseCase

from src.core.di import Container
from src.core.exceptions import (
    ValueObjectException,
    TrackNotFoundError,
    InsufficientPermission
)
from dependency_injector.wiring import inject, Provide
from concurrent import futures
import grpc
from grpc import ServicerContext
from google.protobuf import empty_pb2
import asyncio


class PlaylistCommandService(PlaylistCommands_pb2_grpc.PlaylistCommandServiceServicer):
    @inject
    def __init__(
        self,
        add_track_use_case: AddTrackToPlaylistUseCase = Provide[Container.add_track_use_case],
        add_playlist_use_case: AddPlaylistUseCase = Provide[Container.add_playlist_use_case]
    ):
        self._add_track_use_case = add_track_use_case
        self._add_playlist_use_case = add_playlist_use_case
    
    async def AddTrackToPlaylist(self, request, context: ServicerContext):
        try:
            await self._add_track_use_case.execute(
                playlist_id=request.playlist_id,
                track_id=request.track_id,
                user_id=request.user_id  # из JWT
            )
            return empty_pb2.Empty()

        except InsufficientPermission as e:
            await context.abort(grpc.StatusCode.PERMISSION_DENIED, str(e))
        except ValueObjectException as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except TrackNotFoundError as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def AddPlaylist(self, request, context: ServicerContext):
        try:
            await self._add_playlist_use_case.execute(
                playlist_id=request.playlist_id,
                user_id=request.user_id
            )
            return empty_pb2.Empty()
        except InsufficientPermission as e:
            await context.abort(grpc.StatusCode.PERMISSION_DENIED, str(e))
        except ValueObjectException as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except TrackNotFoundError as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))
    


async def serve_grpc():
   
    server = grpc.aio.server()
    PlaylistCommands_pb2_grpc.add_PlaylistCommandServiceServicer_to_server(
        PlaylistCommandService(), server
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