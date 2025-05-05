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
        register_use_case: RegisterUserUseCase = Provide[Container.register_use_case]
    ):
        self.register_use_case = register_use_case
    
    async def RegisterUser(self, request, context: ServicerContext):
        try:
            user_id = await self.register_use_case.execute(
                email=request.email,
                password=request.password,
                username=request.username
            )
            return commands_pb2.RegisterUserResponse(user_id=user_id)
        
        except ValueObjectException as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except (EmailAlreadyExistsError, UsernameAlreadyExistsError) as e:
            await context.abort(grpc.StatusCode.ALREADY_EXISTS, str(e)) 
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")


    async def RegisterUser(self, request, context):
        try:
            user_id = await self.register_use_case.execute(
                email=request.email,
                password=request.password,
                username=request.username
            )
            return commands_pb2.RegisterUserResponse(user_id=user_id)
        
        except ValueObjectException as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except (EmailAlreadyExistsError, UsernameAlreadyExistsError) as e:
            await context.abort(grpc.StatusCode.ALREADY_EXISTS, str(e)) 
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")


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