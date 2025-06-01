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

from src.core.protos.generated import TrackCommands_pb2, TrackCommands_pb2_grpc
from src.core.di import Container
from src.applications.use_cases.get_tracks import (
    GetTracksByArtistUseCase,
    GetTracksByGenreUseCase
)
from google.protobuf.timestamp_pb2 import Timestamp

class TrackQueryService(TrackCommands_pb2_grpc.TrackQueryServiceServicer):
    def __init__(self):
        self._get_tracks_by_artist_uc = Container.get_tracks_by_artist_use_case()
        self._get_tracks_by_genre_uc = Container.get_tracks_by_genre_use_case()
        # self._get_track_uc = Container.get_track_use_case()

    async def GetTracksByArtist(self, request, context):
        try:
            tracks = await self._get_tracks_by_artist_uc.execute(
                artist_id=request.artist_id,
                offset=request.pagination.offset,
                limit=request.pagination.limit
            )
            
            return TrackCommands_pb2.TrackListResponse(
                tracks=[self._convert_track_to_proto(track) for track in tracks],
                pagination=TrackCommands_pb2.Pagination(
                    total=len(tracks),
                    offset=request.pagination.offset,
                    limit=request.pagination.limit
                )
            )
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

            
    async def GetTracksByGenre(self, request, context):
        
        try:
            tracks = await self._get_tracks_by_genre_uc.execute(
                genre_id=request.genre_id,
                offset=request.pagination.offset,
                limit=request.pagination.limit
            )
            
            return TrackCommands_pb2.TrackListResponse(
                tracks=[self._convert_track_to_proto(track) for track in tracks],
                pagination=TrackCommands_pb2.Pagination(
                    total=len(tracks),
                    offset=request.pagination.offset,
                    limit=request.pagination.limit
                )
            )
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

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

async def serve_grpc():
   
    server = grpc.aio.server()
    TrackCommands_pb2_grpc.add_TrackQueryServiceServicer_to_server(
        TrackQueryService(), server
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