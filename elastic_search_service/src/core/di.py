from dependency_injector import containers, providers

from src.infrastructure.elastic.client import ElasticClient
from src.infrastructure.elastic.elastic_repository import ElasticSearchRepository
from src.applications.use_cases.search_tracks import SearchTracksUseCase


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            # сюда займём future modules, например gRPC-Server
            "src.infrastructure.grpc.server",
        ]
    )

    # 1) Elastic client
    elastic_client = providers.Singleton(
        ElasticClient
    )

    # 2) Репозиторий поиска
    search_repository = providers.Factory(
        ElasticSearchRepository,
        es_client=elastic_client
    )

    # 3) Use Case
    search_tracks_use_case = providers.Factory(
        SearchTracksUseCase,
        search_repo=search_repository
    )

    @classmethod
    async def init_resources(cls):
        es = cls.elastic_client()
        await es.connect()

    @classmethod
    async def shutdown_resources(cls):
        es = cls.elastic_client()
        if es:
            await es.disconnect()
