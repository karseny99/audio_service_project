from dependency_injector import containers, providers
from faststream.kafka import KafkaBroker

from src.applications.use_cases.like_track import LikeTrackUseCase
from src.applications.use_cases.get_user_likes import GetUserLikesUseCase
from src.applications.use_cases.get_history_use_case import GetHistoryUseCase
from src.applications.use_cases.delete_user import HandleUserDeletedUseCase
from src.applications.use_cases.add_track_to_history import HandleTrackListenedUseCase

from src.infrastructure.database.repositories.user_likes_repository import PostgresUserLikesRepository
from src.infrastructure.external.track_service import TrackServiceClient
from src.infrastructure.kafka.publisher import KafkaEventPublisher
from src.infrastructure.kafka.consumer import KafkaConsumer, EventTypeMapping
from src.infrastructure.event_handlers.user_deleted import UserDeletedHandler
from src.infrastructure.event_handlers.track_listened import TrackListenedHandler

from src.core.protos.generated import UserEvents_pb2
from src.core.protos.generated import TrackEvents_pb2
from src.core.protos.generated import StreamEvents_pb2
from src.core.config import settings

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.infrastructure.grpc.server",
            "src.infrastructure.kafka.consumer"
        ]
    )

    # Репозитории to do
    user_likes_repository = providers.Singleton(
        PostgresUserLikesRepository
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
    like_track_use_case = providers.Factory(
        LikeTrackUseCase,
        likes_repo=user_likes_repository,
        track_service=track_service_client,
    )

    get_user_likes_use_case = providers.Factory(
        GetUserLikesUseCase,
        likes_repo=user_likes_repository,
    )

    get_history_use_case = providers.Factory(
        GetHistoryUseCase,
        likes_repo=user_likes_repository,
    )

    handle_user_deleted_use_case = providers.Factory(
        HandleUserDeletedUseCase,
        likes_repo=user_likes_repository
    )

    handle_track_listened_use_case = providers.Factory(
        HandleTrackListenedUseCase,
        likes_repo=user_likes_repository
    )
    
    # # Event Handlers
    user_deleted_handler = providers.Factory(
        UserDeletedHandler,
        use_case=handle_user_deleted_use_case
    )

    track_listened_handler = providers.Factory(
        TrackListenedHandler,
        use_case=handle_track_listened_use_case
    )
    
#     # Настройка маппинга событий
    event_mappings = providers.Dict(
        {
            "UserDeleted": providers.Factory(  # Ключ - строка, которая соответствует event-type из заголовка Kafka
                EventTypeMapping,
                proto_type=providers.Object(UserEvents_pb2.UserDeleted),
                handler=user_deleted_handler
            ),
            "SessionHistory": providers.Factory(  
                EventTypeMapping,
                proto_type=providers.Object(StreamEvents_pb2.SessionHistory),
                handler=track_listened_handler
            ),

        }
    )

    # # Kafka Consumer
    kafka_consumer = providers.Singleton(
        KafkaConsumer,
        broker=kafka_broker,
        topic=settings.KAFKA_LISTENING_HISTORY_TOPIC,
        event_mappings=event_mappings
    )
