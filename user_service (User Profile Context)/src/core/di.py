from dependency_injector import containers, providers
from faststream.kafka import KafkaBroker
from src.infrastructure.database.repositories.user_repository import PostgresUserRepository
from src.infrastructure.cache.redis_repository import RedisCacheRepository
from src.infrastructure.kafka.publisher import KafkaEventPublisher
from src.infrastructure.cache.redis_client import RedisClient


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
    kafka_broker = providers.Singleton(
        KafkaBroker,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )

    kafka_publisher = providers.Singleton(
        KafkaEventPublisher,
        broker=kafka_broker
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
        event_publisher=kafka_publisher,
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
        redis = cls.redis_client()
        await redis.connect()

    @classmethod
    async def shutdown_resources(cls):
        redis = cls.redis_client()
        await redis.disconnect()
        
        publisher = cls.kafka_publisher()
        if publisher:  # Проверка на None
            await publisher.disconnect()