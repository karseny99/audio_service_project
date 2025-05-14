from dependency_injector import containers, providers
from faststream.kafka import KafkaBroker
from src.infrastructure.database.repositories.playlist_repository import PostgresPlaylistRepository
from src.infrastructure.external.track_service import TrackServiceClient
from src.applications.use_cases.add_track import AddTrackToPlaylistUseCase
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

    track_service_client = providers.Singleton(
        TrackServiceClient
    )

    add_track_use_case = providers.Factory(
        AddTrackToPlaylistUseCase,
        playlist_repo=playlist_repository,
        track_service=track_service_client,
        event_publisher=kafka_publisher
    )
    
    @staticmethod
    async def init_resources():
        await Container.track_service_client().connect()
        
    @staticmethod
    async def shutdown_resources():
        await Container.track_service_client().disconnect()
