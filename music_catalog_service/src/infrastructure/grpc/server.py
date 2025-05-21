from src.core.config import settings
from src.core.logger import logger
from src.core.protos.generated import TrackCommands_pb2_grpc, TrackCommands_pb2
# from src.applications.use_cases.add_track import AddTrackToPlaylistUseCase
from src.applications.use_cases.get_track import GetTrackUseCase
from src.core.di import Container
from src.core.exceptions import (
    ValueObjectException,
    TrackNotFound,
    InsufficientPermission
)
from dependency_injector.wiring import inject, Provide
from concurrent import futures
import grpc
from grpc import ServicerContext
from google.protobuf import empty_pb2, timestamp_pb2
import asyncio


class TrackCommamdService(TrackCommands_pb2_grpc.TrackServiceServicer):
    @inject
    def __init__(
        self,
        # add_track_use_case: AddTrackToPlaylistUseCase = Provide[Container.add_track_use_case]
        get_track_use_case: GetTrackUseCase = Provide[Container.get_track_use_case]
    ):
        # self._add_track_use_case = add_track_use_case
        self._get_track_use_case = get_track_use_case
    
    # async def AddTrackToPlaylist(self, request, context: ServicerContext):
    #     try:
    #         await self._add_track_use_case.execute(
    #             playlist_id=request.playlist_id,
    #             track_id=request.track_id,
    #             user_id=request.user_id  # из JWT
    #         )
    #         return empty_pb2.Empty()

    #     except InsufficientPermission as e:
    #         await context.abort(grpc.StatusCode.PERMISSION_DENIED, str(e))
    #     except ValueObjectException as e:
    #         await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
    #     except TrackNotFoundError as e:
    #         await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
    #     except Exception as e:
    #         await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetTrack(self, request, context: ServicerContext):
        try:
            track = await self._get_track_use_case.execute(
                track_id=request.track_id,
            )
            created_at = timestamp_pb2.Timestamp()
            created_at.FromDatetime(track.created_at)
            
            return TrackCommands_pb2.Track(
                track_id=track.track_id,
                title=track.title,
                duration=track.duration,
                artists=[
                    TrackCommands_pb2.ArtistInfo(
                        artist_id=a.artist_id,
                        name=a.name,
                    ) for a in track.artists
                ],
                genres=[
                    TrackCommands_pb2.Genre(
                        genre_id=g.genre_id,
                        name=g.name
                    ) for g in track.genres
                ],
                explicit=track.explicit,
                release_date=track.release_date.isoformat(),
                created_at=created_at
            )

        except ValueObjectException as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except TrackNotFound as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))


    async def GetTracksByArtist(self, request, context):
        try:
            tracks = await self._get_tracks_by_artist_use_case.execute(
                artist_id=request.artist_id,
                offset=request.offset,
                limit=request.limit
            )
            return self._convert_tracks_to_proto(tracks)
        
        except Exception as e:
            raise e
        
    async def GetTracksByGenre(self, request, context):
        try:
            tracks = await self._get_tracks_by_genre_use_case.execute(
                genre_id=request.genre_id,
                offset=request.offset,
                limit=request.limit
            )
            return self._convert_tracks_to_proto(tracks)
        except Exception as e:
            raise e

async def serve_grpc():
   
    server = grpc.aio.server()
    TrackCommands_pb2_grpc.add_TrackServiceServicer_to_server(
        TrackCommamdService(), server
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