from .kafka_producer import KafkaProducer
from dependency_injector import containers, providers
from grpc_clients.user_client import get_user_stub


class Container(containers.DeclarativeContainer):
    kafka_producer = providers.Singleton(KafkaProducer)

    wiring_config = containers.WiringConfiguration(
        packages=["src.api.v1"]
    )

    # декларируем gRPC stub как синглтон
    user_stub = providers.Singleton(get_user_stub)