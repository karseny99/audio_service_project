from dependency_injector import containers, providers
from src.infrastructure.elastic.client import ElasticClient
from src.infrastructure.elastic.elastic_repository import ElasticSearchRepository
from src.applications.use_cases.search_tracks import SearchTracksUseCase
from src.infrastructure.cache.redis_client import RedisClient
from src.infrastructure.cache.redis_repository import RedisCacheRepository
from src.infrastructure.cache.serialization import DomainJsonSerializer

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["src.infrastructure.grpc.server"]
    )

    elastic_client = providers.Singleton(
        ElasticClient
    )
    
    search_repository = providers.Factory(
        ElasticSearchRepository,
        es_client=elastic_client.provided.client  # Используем свойство client
    )

    redis_client = providers.Singleton(RedisClient)
    
    cache_repo = providers.Factory(
        RedisCacheRepository,
        redis=redis_client
    )
    
    cache_serializer = providers.Factory(DomainJsonSerializer)

    search_tracks_use_case = providers.Factory(
        SearchTracksUseCase,
        search_repo=search_repository,
        _cache_repo=cache_repo,
        _cache_serializer=cache_serializer
    )

    @classmethod
    async def init_resources(cls):
        es = cls.elastic_client()
        await es.connect()
        
        redis = cls.redis_client()
        await redis.connect()

    @classmethod
    async def shutdown_resources(cls):
        es = cls.elastic_client()
        if es:
            await es.disconnect()

        redis = cls.redis_client()
        if redis:
            await redis.disconnect()