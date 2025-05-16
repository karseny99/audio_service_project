from dependency_injector import containers, providers
from faststream.kafka import KafkaBroker

from src.applications.use_cases.add_track import AddTrackToPlaylistUseCase
from src.applications.use_cases.delete_user import HandleUserDeletedUseCase

from src.infrastructure.database.repositories.playlist_repository import PostgresPlaylistRepository
from src.infrastructure.external.track_service import TrackServiceClient
from src.infrastructure.kafka.publisher import KafkaEventPublisher
from src.infrastructure.kafka.consumer import KafkaConsumer, EventTypeMapping
from src.infrastructure.event_handlers.user_deleted import UserDeletedHandler

from src.core.protos.generated import UserEvents_pb2
from src.core.config import settings

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.infrastructure.grpc.server",
            "src.infrastructure.kafka.consumer"
        ]
    )

    # Репозитории
    playlist_repository = providers.Singleton(
        PostgresPlaylistRepository
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

    # gRPC клиенты
    track_service_client = providers.Singleton(
        TrackServiceClient
    )

    # Use Cases
    add_track_use_case = providers.Factory(
        AddTrackToPlaylistUseCase,
        playlist_repo=playlist_repository,
        track_service=track_service_client,
        event_publisher=kafka_publisher
    )

    handle_user_deleted_use_case = providers.Factory(
        HandleUserDeletedUseCase,
        playlist_repo=playlist_repository
    )
    
    # Event Handlers
    user_deleted_handler = providers.Factory(
        UserDeletedHandler,
        use_case=handle_user_deleted_use_case
    )
    
    # Настройка маппинга событий
    event_mappings = providers.Dict(
    {
        "UserDeleted": providers.Factory(  # Ключ - строка, которая соответствует event-type из заголовка Kafka
            EventTypeMapping,
            proto_type=providers.Object(UserEvents_pb2.UserDeleted),
            handler=user_deleted_handler
        ),
    }
)

    # Kafka Consumer
    kafka_consumer = providers.Singleton(
        KafkaConsumer,
        broker=kafka_broker,
        topic=settings.KAFKA_PLAYLIST_CONTEXT_TOPIC,
        event_mappings=event_mappings
    )
