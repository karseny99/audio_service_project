from aiobotocore.session import get_session
from dependency_injector import containers, providers
from faststream.kafka import KafkaBroker


from src.applications.use_cases.get_session import GetSessionUseCase
from src.applications.use_cases.save_session import SaveSessionUseCase
from src.applications.use_cases.chunk_generator import GetChunkGeneratorUseCase
from src.applications.use_cases.ack_chunks import AcknowledgeChunksUseCase
from src.applications.use_cases.control_session import (
    PauseSessionUseCase,
    ResumeSessionUseCase,
    StopSessionUseCase,
    ChangeSessionBitrateUseCase,
    ChangeSessionOffsetUseCase,

)
from src.infrastructure.storage.audio_streamer import S3AudioStreamer
from src.infrastructure.database.redis_repository import RedisStreamingRepository
from src.infrastructure.kafka.publisher import KafkaEventPublisher
from src.infrastructure.database.redis_client import RedisClient
from src.infrastructure.events.converters import SessionEventConverters
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
    kafka_broker = providers.Singleton(
        KafkaBroker,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )

    kafka_publisher = providers.Singleton(
        KafkaEventPublisher,
        broker=kafka_broker,
        destination=[settings.KAFKA_ETL_TOPIC],
        converters=SessionEventConverters,
    )

    history_kafka_publisher = providers.Singleton(
        KafkaEventPublisher,
        broker=kafka_broker,
        destination=[settings.KAFKA_LISTENING_HISTORY_CONTEXT_TOPIC],
        converters=SessionEventConverters,
    )

    # redis
    redis_client = providers.Singleton(
        RedisClient
    )

    session_repo = providers.Factory(
        RedisStreamingRepository,
        redis_client=redis_client
    )
    

    # minio 
    audio_streamer = providers.Singleton(
        S3AudioStreamer,
        bucket_name=settings.MINIO_TRACK_BUCKET,
        aws_access_key_id=settings.MINIO_USER,
        aws_secret_access_key=settings.MINIO_PASSWORD,
        endpoint_url=settings.MINIO_URL,
        chunk_size=settings.MINIO_DEFAULT_CHUNK_SIZE,
        path=settings.MINIO_TRACK_PATH,
    )


    '''

        USE CASE GET SESSION
    
    '''
    
    get_session_use_case = providers.Factory(
        GetSessionUseCase, 
        session_repo=session_repo,  
        audio_streamer=audio_streamer,
        event_publisher=kafka_publisher,
    )
    
    get_save_session_use_case = providers.Factory(
        SaveSessionUseCase, 
        session_repo=session_repo,  
    )

    get_chunk_generator_use_case = providers.Factory(
        GetChunkGeneratorUseCase,
        audio_streamer=audio_streamer
    )

    get_ack_chunks_use_case = providers.Factory(
        AcknowledgeChunksUseCase,
        event_publisher=kafka_publisher,
    )

    get_pause_session_use_case = providers.Factory(
        PauseSessionUseCase,
        session_repo=session_repo, 
        event_publisher=kafka_publisher,
    )

    get_resume_session_use_case = providers.Factory(
        ResumeSessionUseCase,
        session_repo=session_repo, 
        event_publisher=kafka_publisher,
    )

    get_stop_session_use_case = providers.Factory(
        StopSessionUseCase,
        session_repo=session_repo, 
        event_publisher=kafka_publisher,
        history_event_publisher=history_kafka_publisher,
    )

    get_change_session_bitrate_use_case = providers.Factory(
        ChangeSessionBitrateUseCase,
        session_repo=session_repo, 
        audio_streamer=audio_streamer,
        event_publisher=kafka_publisher,
    )

    get_change_session_offset_use_case = providers.Factory(
        ChangeSessionOffsetUseCase,
        session_repo=session_repo, 
        audio_streamer=audio_streamer,
        event_publisher=kafka_publisher,
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