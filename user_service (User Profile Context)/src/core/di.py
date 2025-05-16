from dependency_injector import containers, providers
from faststream.kafka import KafkaBroker
from src.infrastructure.database.repositories.user_repository import PostgresUserRepository
from src.infrastructure.events.converters import UserEventConverters
from src.domain.users.services import UserRegistrationService
from src.applications.use_cases.register_user import RegisterUserUseCase
from src.infrastructure.kafka.publisher import KafkaEventPublisher
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

    kafka_publisher_register_uc = providers.Singleton(
        KafkaEventPublisher,
        broker=kafka_broker,
        destination=[settings.KAFKA_PLAYLIST_CONTEXT_TOPIC, settings.KAFKA_LISTENING_HISTORY_CONTEXT_TOPIC],
        converters=UserEventConverters,
    )

    # Use Cases
    register_use_case = providers.Factory(
        RegisterUserUseCase,
        user_repo=user_repository,
        event_publisher=kafka_publisher_register_uc,
        registration_service=registration_service
    )

    @classmethod
    async def init_resources(cls):
        """Инициализация всех ресурсов"""
        await cls.kafka_publisher_register_uc().connect()
        await cls.kafka_broker().start()
        # Инициализация других ресурсов при необходимости

    @classmethod
    async def shutdown_resources(cls):
        """Корректное завершение всех ресурсов"""
        publisher = cls.kafka_publisher_register_uc()
        if publisher:  # Проверка на None
            await publisher.disconnect()
