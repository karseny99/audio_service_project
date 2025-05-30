from dependency_injector import containers, providers
from faststream.kafka import KafkaBroker
from minio import Minio

from src.applications.use_cases.get_session import GetSessionUseCase
from src.applications.use_cases.chunk_generator import GetChunkGeneratorUseCase
from src.infrastructure.storage.audio_streamer import S3AudioStreamer
from src.infrastructure.cache.redis_repository import RedisCacheRepository
# from src.infrastructure.kafka.publisher import KafkaEventPublisher
from src.infrastructure.cache.redis_client import RedisClient
# from src.infrastructure.events.converters import UserEventConverters
from src.infrastructure.cache.serialization import DomainJsonSerializer
# from src.infrastructure.cache.user_serializer import UserSerializer, SimpleSerializer

from src.core.config import settings

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.infrastructure.grpc.server",
            "src.infrastructure.storage.audio_streamer"
            # другие модули, где используется DI
        ]
    )

    # Kafka зависимости
    # Этого брокера надо создавать отдельно для консумера
    # иначе будет плохо
    kafka_broker = providers.Singleton(
        KafkaBroker,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )

    # kafka_publisher = providers.Singleton(
    #     KafkaEventPublisher,
    #     broker=kafka_broker,
    #     destination=settings.KAFKA_USER_CONTEXT_TOPIC, # just to fill the argument
    #     converters=UserEventConverters,
    # )

    # redis
    redis_client = providers.Singleton(
        RedisClient
    )

    cache_repository = providers.Factory(
        RedisCacheRepository,
        redis=redis_client
    )


    cache_serializer = providers.Singleton(
        DomainJsonSerializer
    )
    
    # user_serializer = providers.Factory(
    #     UserSerializer,
    #     base_serializer=cache_serializer
    # )
    
    # simple_serializer = providers.Factory(
    #     SimpleSerializer,
    #     base_serializer=cache_serializer
    # )


    # minio storage ** experimental **
    minio_client = providers.Factory(
        Minio,
        endpoint=settings.MINIO_URL,
        access_key=settings.MINIO_USER,
        secret_key=settings.MINIO_PASSWORD,
        secure=False
    )

    audio_streamer = providers.Singleton(
        S3AudioStreamer,
        bucket_name=settings.MINIO_TRACK_BUCKET,
        minio_client=minio_client,
        chunk_size=settings.MINIO_DEFAULT_CHUNK_SIZE,
        path=settings.MINIO_TRACK_PATH,
    )


    '''

        USE CASE GET SESSION
    
    '''
    
    get_session_use_case = providers.Factory(
        GetSessionUseCase, 
        session_repo=redis_client,
        audio_streamer=audio_streamer,
    )

    get_chunk_generator_use_case = providers.Factory(
        GetChunkGeneratorUseCase,
        audio_streamer=audio_streamer
    )

    @classmethod
    async def init_resources(cls):
        # publisher = cls.kafka_publisher()
        # await publisher.connect()
        
        redis = cls.redis_client()
        await redis.connect()

    @classmethod
    async def shutdown_resources(cls):
        redis = cls.redis_client()
        await redis.disconnect()


        
        # publisher = cls.kafka_publisher()
        # if publisher:
            # await publisher.disconnect()