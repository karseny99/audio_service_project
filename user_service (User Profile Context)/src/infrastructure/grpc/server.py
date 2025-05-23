from google.protobuf.empty_pb2 import Empty
from grpc import StatusCode
from dependency_injector.wiring import inject, Provide
import grpc
import asyncio

from src.core.di import Container
from src.core.protos.generated import commands_pb2, commands_pb2_grpc
from src.core.di import Container
from src.core.exceptions import (
    ValueObjectException,
    UserNotFoundError,
    InvalidPasswordError,
    EmailAlreadyExistsError, 
    UsernameAlreadyExistsError
)

from src.core.config import settings
from src.core.logger import logger

from google.protobuf import timestamp_pb2

class UserCommandService(commands_pb2_grpc.UserCommandServiceServicer):
    @inject
    def __init__(
            self,
            register_uc = Provide[Container.register_use_case],
            change_password_uc = Provide[Container.change_password_use_case],
            auth_uc = Provide[Container.auth_user_use_case],
            get_user_info_uc = Provide[Container.get_user_info_use_case]
    ):
        self._register_uc = register_uc
        self._change_uc = change_password_uc
        self._auth_uc = auth_uc
        self._get_user_info_uc = get_user_info_uc

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
        except (UsernameAlreadyExistsError, EmailAlreadyExistsError) as e:
            await context.abort(StatusCode.ALREADY_EXISTS, str(e))
        except Exception as e:
            await context.abort(StatusCode.INTERNAL, f"Internal error: {e}")

    async def AuthenticateUser(self, request, context):
        try:
            user_id = await self._auth_uc.execute(
                username=request.username,
                password=request.password,
            )
            return commands_pb2.AuthenticateUserResponse(user_id=user_id)
        
        except ValueObjectException as e:
            await context.abort(StatusCode.INVALID_ARGUMENT, str(e))
        except UserNotFoundError as e:            
            await context.abort(StatusCode.NOT_FOUND, str(e))
        except InvalidPasswordError as e:
            await context.abort(StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            await context.abort(StatusCode.INTERNAL, f"Internal error: {e}")


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

    async def GetUserInfo(self, request, context):
        try:
            user = await self._get_user_info_uc.execute(user_id=request.user_id)

            created_at = timestamp_pb2.Timestamp()
            created_at.FromDatetime(user.created_at)
            
            return commands_pb2.GetUserInfoResponse(            
                user_id = user.id,
                username = user.username,
                email = user.email,
                created_at = created_at
            )
        
        except ValueObjectException as e:
            await context.abort(StatusCode.INVALID_ARGUMENT, str(e))
        except UserNotFoundError as e:            
            await context.abort(StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            await context.abort(StatusCode.INTERNAL, f"Internal error: {e}")


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