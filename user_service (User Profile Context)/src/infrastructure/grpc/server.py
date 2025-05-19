from src.core.config import settings
from src.core.logger import logger
from src.applications.use_cases.register_user import RegisterUserUseCase
from src.core.protos.generated import commands_pb2
from src.core.protos.generated import commands_pb2_grpc
from src.core.di import Container
from src.core.exceptions import (
    ValueObjectException,
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError
)

from google.protobuf.empty_pb2 import Empty
from grpc import StatusCode
from dependency_injector.wiring import inject, Provide
from src.core.di import Container
from src.core.protos.generated import commands_pb2, commands_pb2_grpc
from src.core.exceptions import ValueObjectException, UserNotFoundError, InvalidPasswordError

from google.protobuf.empty_pb2 import Empty
from src.domain.users.value_objects.password_hash import PasswordHash
from src.infrastructure.database.repositories.user_repository import PostgresUserRepository
from grpc import StatusCode
from dependency_injector.wiring import inject, Provide
from concurrent import futures
import grpc
from grpc import ServicerContext
import signal
import asyncio

class UserCommandService(commands_pb2_grpc.UserCommandServiceServicer):
    @inject
    def __init__(
            self,
            register_uc=Provide[Container.register_use_case],
            change_password_uc=Provide[Container.change_password_use_case],
            user_repo: PostgresUserRepository = Provide[Container.user_repository],
    ):
        self._register_uc = register_uc
        self._repo = user_repo
        self._change_uc = change_password_uc

    async def RegisterUser(self, request, context):
        try:
            user_id = await self._register_uc.execute(
                email=request.email,
                password=request.password,
                username=request.username
            )
            return commands_pb2.RegisterUserResponse(user_id=user_id)

        except ValueObjectException as e:
            await context.abort(StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            await context.abort(StatusCode.INTERNAL, f"Internal error: {e}")

    async def AuthenticateUser(self, request, context):
        repo = PostgresUserRepository()
        user = await repo.get_by_username(request.username)
        if user is None:
            await context.abort(StatusCode.NOT_FOUND, "User not found")

        if request.password != user.password_hash.value:
            await context.abort(StatusCode.INVALID_ARGUMENT, "Invalid credentials")
        
        return commands_pb2.AuthenticateUserResponse(user_id=str(user.id))

    async def ChangePassword(self, request, context):
        try:
            await self._change_uc.execute(
                user_id=int(request.user_id),
                old_password=request.old_password,
                new_password=request.new_password
            )
            return Empty()

        except UserNotFoundError:
            await context.abort(StatusCode.NOT_FOUND, "User not found")
        except InvalidPasswordError as e:
            await context.abort(StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as ex:
            logger.exception("Unexpected error in ChangePassword")
            await context.abort(StatusCode.INTERNAL, "Internal server error")


async def serve_grpc():
    # Инициализация publisher
    
    server = grpc.aio.server()
    commands_pb2_grpc.add_UserCommandServiceServicer_to_server(
        UserCommandService(), server
    )
    server.add_insecure_port(settings.get_grpc_url())
    
    await server.start()
    logger.info(f"gRPC server started on {settings.get_grpc_url()}")
    
    try:
        while True:
            await asyncio.sleep(3600)  # Бесконечное ожидание
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Shutting down server...")
        await server.stop(5)
        logger.info("Server shutdown complete")