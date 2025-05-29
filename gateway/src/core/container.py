from dependency_injector import containers, providers
from src.core.dependencies.grpc_clients import get_user_command_stub
from src.core.dependencies.grpc_clients import get_music_catalog_stub

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["src.api.v1"]
    )

    # декларируем gRPC stub как синглтон
    user_stub = providers.Singleton(get_user_command_stub)

    music_catalog_stub = providers.Singleton(get_music_catalog_stub)
