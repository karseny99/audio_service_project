# user_service/src/core/di.py

from dependency_injector import containers, providers
from src.infrastructure.database.repositories.user_repository import PostgresUserRepository
from src.infrastructure.kafka.publisher import KafkaEventPublisher
from src.domain.events.publisher import EventPublisher
from src.applications.use_cases.register_user import RegisterUserUseCase
from src.applications.use_cases.change_password import ChangePasswordUseCase
from src.domain.users.services import UserRegistrationService

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["src.infrastructure.grpc.server"]
    )

    # репозиторий и kafka publisher
    user_repository = providers.Singleton(PostgresUserRepository)
    kafka_publisher = providers.Singleton(KafkaEventPublisher, broker=providers.Factory(...))

    # use cases
    register_use_case = providers.Factory(
        RegisterUserUseCase,
        user_repo=user_repository,
        event_publisher=kafka_publisher,
        registration_service=providers.Singleton(UserRegistrationService),
    )

    change_password_use_case = providers.Factory(
        ChangePasswordUseCase,
        user_repo=user_repository,
        event_publisher=kafka_publisher
    )
