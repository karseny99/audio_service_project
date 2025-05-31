# src/infrastructure/grpc/server.py

import grpc
import asyncio
from concurrent import futures
from grpc import ServicerContext
from src.core.config import settings
from src.core.logger import logger
from src.core.di import Container

# Импортируем сгенерированные файлы из track_search.proto
from src.core.protos.generated.track_search_pb2 import (
    SearchTracksResponse,
    TrackItem as ProtoTrackItem
)
from src.core.protos.generated.track_search_pb2_grpc import (
    TrackSearchServiceServicer,
    add_TrackSearchServiceServicer_to_server
)
from src.applications.use_cases.search_tracks import ElasticTrackRequest
from src.core.exceptions import DomainError

class TrackSearchService(TrackSearchServiceServicer):
    """
    gRPC-сервис для поиска треков.
    """
    def __init__(self):
        # Инжектим UseCase из контейнера
        self._search_uc = Container.search_tracks_use_case()

    async def Search(self, request, context: ServicerContext) -> SearchTracksResponse:
        try:
            # Конвертируем gRPC-запрос в Pydantic-модель
            req = ElasticTrackRequest(
                title=request.title or None,
                artist_name=request.artist_name or None,
                genre_name=list(request.genre_name) if request.genre_name else None,
                min_duration_ms=request.min_duration_ms if request.min_duration_ms != 0 else None,
                max_duration_ms=request.max_duration_ms if request.max_duration_ms != 0 else None,
                explicit=(request.explicit if context.invocation_metadata() else None),
                release_date_from=(request.release_date_from or None),
                release_date_to=(request.release_date_to or None),
                page=request.page or 1,
                page_size=request.page_size or 50
            )

            response = await self._search_uc.execute(req)

            proto_tracks = []
            for t in response.tracks:
                proto_tracks.append(
                    ProtoTrackItem(
                        track_id=t.track_id or 0,
                        title=t.title or "",
                        duration_ms=t.duration_ms or 0,
                        artists=t.artists or [],
                        genres=t.genres or [],
                        explicit=t.explicit if t.explicit is not None else False,
                        release_date=(t.release_date.isoformat() if t.release_date else "")
                    )
                )

            return SearchTracksResponse(
                tracks=proto_tracks,
                total=response.total,
                page=response.page,
                page_size=response.page_size,
                success=True
            )

        except DomainError as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

async def serve_grpc():
    server = grpc.aio.server()
    add_TrackSearchServiceServicer_to_server(TrackSearchService(), server)
    server.add_insecure_port(settings.get_grpc_url())
    await server.start()
    logger.info(f"gRPC TrackSearch service started on {settings.get_grpc_url()}")

    try:
        while True:
            await asyncio.sleep(3600)
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Shutting down TrackSearch gRPC server...")
        await server.stop(5)
