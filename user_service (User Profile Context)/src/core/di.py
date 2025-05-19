from dependency_injector import containers, providers
from faststream.kafka import KafkaBroker
from src.infrastructure.database.repositories.user_repository import PostgresUserRepository
from src.infrastructure.kafka.publisher import KafkaEventPublisher

from src.domain.users.services import UserRegistrationService
from src.applications.use_cases.register_user import RegisterUserUseCase
from src.applications.use_cases.change_password import ChangePasswordUseCase
from src.applications.use_cases.auth_user import AuthUserUseCase

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
    )