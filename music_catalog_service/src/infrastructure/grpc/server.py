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
        self._get_track_uc = Container.get_track_use_case()

    async def GetTracksByArtist(self, request, context):
        try:
            tracks = await self._get_tracks_by_artist_uc.execute(
                artist_id=request.artist_id,
                offset=request.pagination.offset,
                limit=request.pagination.limit
            )
            response = TrackCommands_pb2.TrackListResponse(
                tracks=[self._convert_track_to_proto(track) for track in tracks],
                pagination=TrackCommands_pb2.Pagination(
                    total=len(tracks),
                    offset=request.pagination.offset,
                    limit=request.pagination.limit
                )
            )
            return response
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

            
    async def GetTracksByGenre(self, request, context):
        
        try:
            tracks = await self._get_tracks_by_genre_uc.execute(
                genre_id=request.genre_id,
                offset=request.pagination.offset,
                limit=request.pagination.limit
            )
            
            response = TrackCommands_pb2.TrackListResponse(
                tracks=[self._convert_track_to_proto(track) for track in tracks],
                pagination=TrackCommands_pb2.Pagination(
                    total=len(tracks),
                    offset=request.pagination.offset,
                    limit=request.pagination.limit
                )
            )
            return response
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetTrack(self, request, context: ServicerContext):
        try:
            logger.debug(f"{request.track_id} received")
            track = await self._get_track_uc.execute(
                track_id=request.track_id,
            )

            logger.debug(track)

            created_at = timestamp_pb2.Timestamp()
            created_at.FromDatetime(track.created_at)
            
            return self._convert_track_to_proto(track)

        except ValueObjectException as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except TrackNotFound as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def VerifyTrackExists(self, request, context: ServicerContext):
        try:
            try:
                track = await self._get_track_uc.execute(
                    track_id=request.track_id,
                )
            except TrackNotFound:
                return TrackCommands_pb2.VerifyTrackResponse(exists=False)

            return TrackCommands_pb2.VerifyTrackResponse(exists=True)
        except ValueObjectException as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def _convert_track_to_proto(self, track) -> TrackCommands_pb2.Track:
        # Преобразование даты создания в protobuf Timestamp
        created_at = Timestamp()
        created_at.FromDatetime(track.created_at)
        
        # Основные поля трека
        proto_track = TrackCommands_pb2.Track(
            track_id=track.track_id,
            title=track.title,
            duration_ms=track.duration.value if track.duration else 0,
            explicit=track.explicit,
            release_date=track.release_date.isoformat() if track.release_date else "",
            created_at=created_at
        )
        
        # Добавление артистов
        for artist in track.artists:
            proto_track.artists.append(
                TrackCommands_pb2.Artist(
                    artist_id=artist.artist_id,
                    name=artist.name,
                    is_verified=artist.is_verified
                )
            )
        
        # Добавление жанров
        for genre in track.genres:
            proto_track.genres.append(
                TrackCommands_pb2.Genre(
                    genre_id=genre.genre_id,
                    name=genre.name
                )
            )
        
        return proto_track


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