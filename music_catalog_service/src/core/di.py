from dependency_injector import containers, providers
from faststream.kafka import KafkaBroker

# from src.applications.use_cases.add_track import AddTrackToPlaylistUseCase
from src.applications.use_cases.get_track import GetTrackUseCase

from src.infrastructure.database.repositories.music_repository import PostgresMusicRepository
from src.infrastructure.cache.redis_repository import RedisCacheRepository
from src.infrastructure.kafka.publisher import KafkaEventPublisher

# from src.infrastructure.events.converters import UserEventConverter
from src.infrastructure.events.base_converter import BaseEventConverter

from src.infrastructure.cache.serialization import DomainJsonSerializer
from src.infrastructure.cache.track_serializer import TrackSerializer
from src.infrastructure.cache.redis_client import RedisClient


from src.core.protos.generated import UserEvents_pb2
from src.core.config import settings

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.infrastructure.grpc.server",
            "src.infrastructure.kafka.consumer"
        ]
    )

    '''     POSTGRES    '''
    music_repository = providers.Singleton(
        PostgresMusicRepository
    )
    '''     POSTGRES    '''
    
    
    '''     KAFKA BROKER     '''
    # Kafka зависимости
    kafka_broker = providers.Singleton(
        KafkaBroker,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )
    '''     KAFKA BROKER     '''


    '''     KAFKA PUBLISHER     '''
    # Kafka publisher (use another for each use case, cuz public topics could differ)
    kafka_publisher = providers.Singleton(
        KafkaEventPublisher,
        broker=kafka_broker,
        destination=[settings.KAFKA_PLAYLIST_CONTEXT_TOPIC],
        converters=BaseEventConverter,
                # TODO: not valid code now cuz imported abstract converter
                # needs specialization for playlist's events 
                # - check event converter for that in user_service/src/infra/events/ 
    )

    # kafka_publisher_register_uc = providers.Singleton(
    #     KafkaEventPublisher,
    #     broker=kafka_broker,
    #     destination=[settings.KAFKA_PLAYLIST_CONTEXT_TOPIC],
    #     converters=UserEventConverter,
    # )
    '''     KAFKA PUBLISHER     '''




    '''     GRPC CLIENT     '''
    # gRPC клиенты
    # track_service_client = providers.Singleton(
    #     TrackServiceClient
    # )
    '''     GRPC CLIENT     '''




    '''     USE CASES       '''
    # Use Cases
    # add_track_use_case = providers.Factory(
    #     AddTrackToPlaylistUseCase,
    #     playlist_repo=music_repository,
    #     track_service=track_service_client,
    #     event_publisher=kafka_publisher
    # )

    '''     USE CASES      '''

    

    '''     KAFKA CONSUMER     '''
    # Настройка маппинга событий
    # event_mappings = providers.Dict(
    #     {
    #         "UserDeleted": providers.Factory(  # Ключ - строка, которая соответствует event-type из заголовка Kafka
    #             EventTypeMapping,
    #             proto_type=providers.Object(UserEvents_pb2.UserDeleted),
    #             handler=user_deleted_handler
    #         ),
    #     }
    # )

    # # Kafka Consumer 
    # kafka_consumer = providers.Singleton(
    #     KafkaConsumer,
    #     broker=kafka_broker,
    #     topic=settings.KAFKA_PLAYLIST_CONTEXT_TOPIC,
    #     event_mappings=event_mappings
    # )
    '''     KAFKA CONSUMER     '''




    '''     CACHE       '''

    redis_client = providers.Singleton(
        RedisClient
    )

    cache_repository = providers.Factory(
        RedisCacheRepository,
        redis=redis_client  # Передаем провайдер без вызова
    )


    cache_serializer = providers.Singleton(
        DomainJsonSerializer
    )
    
    track_serializer = providers.Factory(
        TrackSerializer,  # Специализированный сериализатор для треков
        base_serializer=cache_serializer
    )

    # cache_repository = providers.Singleton(
    #     RedisCacheRepository,
    #     redis=redis_client()  # Обратите внимание на скобки - получаем экземпляр
    # )


    '''     CACHE       '''
    


    '''     USE CASE    '''
    get_track_use_case = providers.Factory(
        GetTrackUseCase,
        music_repo=music_repository,
        cache_repo=cache_repository,
        cache_serializer=track_serializer
    )
    '''     USE CASE    '''



    @classmethod
    async def init_resources(cls):
        redis = cls.redis_client()
        await redis.connect()

    @classmethod
    async def shutdown_resources(cls):
        redis = cls.redis_client()
        await redis.disconnect()
        
        publisher = cls.kafka_publisher()
        if publisher:  # Проверка на None
            await publisher.disconnect()



