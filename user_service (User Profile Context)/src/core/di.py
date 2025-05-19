from dependency_injector import containers, providers
from faststream.kafka import KafkaBroker
from src.infrastructure.database.repositories.user_repository import PostgresUserRepository
from src.infrastructure.cache.redis_repository import RedisCacheRepository
from src.infrastructure.kafka.publisher import KafkaEventPublisher
from src.infrastructure.cache.redis_client import RedisClient


from src.infrastructure.events.converters import UserEventConverters
from src.domain.users.services import UserRegistrationService

from src.applications.use_cases.register_user import RegisterUserUseCase
from src.applications.use_cases.change_password import ChangePasswordUseCase
from src.applications.use_cases.auth_user import AuthUserUseCase

from src.infrastructure.cache.serialization import DomainJsonSerializer
from src.infrastructure.cache.user_serializer import UserSerializer, SimpleSerializer

from src.core.config import settings

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.infrastructure.grpc.server",
            # другие модули, где используется DI
        ]
    )

    # Репозитории
    user_repository = providers.Singleton(
        PostgresUserRepository
    )

    # Сервисы доменной логики
    registration_service = providers.Singleton(
        UserRegistrationService
    )

    # Kafka зависимости
    # Этого брокера надо создавать отдельно для консумера
    # иначе будет плохо
    kafka_broker = providers.Singleton(
        KafkaBroker,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )

    kafka_publisher = providers.Singleton(
        broker=kafka_broker,
        destination=settings.KAFKA_USER_CONTEXT_TOPIC, # just to fill the argument
        converters=UserEventConverters,
    )

    kafka_publisher_register_uc = providers.Singleton(
        KafkaEventPublisher,
        broker=kafka_broker,
        destination=[settings.KAFKA_PLAYLIST_CONTEXT_TOPIC, settings.KAFKA_LISTENING_HISTORY_CONTEXT_TOPIC],
        converters=UserEventConverters,
    )


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
    
    user_serializer = providers.Factory(
        UserSerializer,
        base_serializer=cache_serializer
    )
    
    simple_serializer = providers.Factory(
        SimpleSerializer,
        base_serializer=cache_serializer
    )


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
    
    user_serializer = providers.Factory(
        UserSerializer,
        base_serializer=cache_serializer
    )
    
    simple_serializer = providers.Factory(
        SimpleSerializer,
        base_serializer=cache_serializer
    )

    # Use Cases
    register_use_case = providers.Factory(
        RegisterUserUseCase,
        user_repo=user_repository,
        event_publisher=kafka_publisher_register_uc,
        registration_service=registration_service
    )

    change_password_use_case = providers.Factory(
        ChangePasswordUseCase,
        user_repo=user_repository,
        event_publisher=kafka_publisher
    )

    auth_user_use_case = providers.Factory(
        AuthUserUseCase,
        user_repo=user_repository,
        cache_repo=cache_repository,
        cache_serializer=simple_serializer
    )

    @classmethod
    async def init_resources(cls):
        publisher = cls.kafka_publisher()
        publisher_reg_uc = cls.kafka_publisher_register_uc()
        await publisher.connect()
        await publisher_reg_uc.connect()
        
        redis = cls.redis_client()
        await redis.connect()

    @classmethod
    async def shutdown_resources(cls):
        redis = cls.redis_client()
        await redis.disconnect()


        
        publisher = cls.kafka_publisher()
        publisher_reg_uc = cls.kafka_publisher_register_uc()
        if publisher:  # Проверка на None
            await publisher.disconnect()
        if publisher_reg_uc:
            await publisher_reg_uc.disconnect()