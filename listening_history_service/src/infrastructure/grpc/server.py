from src.core.config import settings
from src.core.logger import logger
from src.core.protos.generated import LikeCommands_pb2_grpc, LikeCommands_pb2
from src.applications.use_cases.like_track import LikeTrackUseCase
from src.applications.use_cases.get_user_likes import GetUserLikesUseCase
from src.applications.use_cases.get_history_use_case import GetHistoryUseCase
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


class LikeCommandService(LikeCommands_pb2_grpc.LikeCommandServiceServicer):
    @inject
    def __init__(
        self,
        add_track_use_case: LikeTrackUseCase = Provide[Container.like_track_use_case],
        get_user_likes_use_case: GetUserLikesUseCase = Provide[Container.get_user_likes_use_case],
        get_history_use_case: GetHistoryUseCase = Provide[Container.get_history_use_case],
    ):
        self._add_track_use_case = add_track_use_case
        self._get_user_likes_use_case = get_user_likes_use_case
        self._get_history_use_case = get_history_use_case
    
    async def LikeTrack(self, request, context: ServicerContext):
        try:
            await self._add_track_use_case.execute(
                track_id=request.track_id,
                user_id=request.user_id
            )
            return empty_pb2.Empty()
        except ValueObjectException as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except TrackNotFoundError as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetUserHistory(self, request, context: ServicerContext):
        try:
            tracks = await self._get_history_use_case.execute(
                user_id=request.user_id,
                count=request.limit,
                offset=request.offset
            )

            return LikeCommands_pb2.GetUserHistoryResponse(
                tracks=[track_id.track_id for track_id in tracks.history],
            )
        except ValueObjectException as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetUserLikes(self, request, context: ServicerContext):
        try:
            logger.debug(request)
            track_ids = await self._get_user_likes_use_case.execute(
                user_id=int(request.user_id),
                count=request.limit,
                offset=request.offset
            )

            logger.debug(track_ids)
            return LikeCommands_pb2.GetUserLikesResponse(
                tracks=[track_id for track_id in track_ids],
            )

        except ValueObjectException as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))


async def serve_grpc():

    server = grpc.aio.server()
    LikeCommands_pb2_grpc.add_LikeCommandServiceServicer_to_server(
        LikeCommandService(), server
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