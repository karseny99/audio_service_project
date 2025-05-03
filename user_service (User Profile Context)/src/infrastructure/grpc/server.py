from src.core.config import settings

from src.applications.use_cases.register_user import RegisterUserUseCase
from src.infrastructure.database.repositories.user_repository import PostgresUserRepository
from src.domain.users.services import UserRegistrationService
from src.core.protos.generated import commands_pb2
from src.core.protos.generated import commands_pb2_grpc
from src.core.exceptions import ValueObjectException, EmailAlreadyExistsError, UsernameAlreadyExistsError

from concurrent import futures
import grpc
import signal
import asyncio

class UserCommandService(commands_pb2_grpc.UserCommandServiceServicer):
    '''
        Proto stuff
    '''
    def __init__(self):
        self.register_use_case = RegisterUserUseCase(
            user_repo=PostgresUserRepository(),
            # event_publisher=Kafka(),
            registration_service=UserRegistrationService
        )

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
    '''
        Запуск grpc сервера
    '''

    server = grpc.aio.server(futures.ThreadPoolExecutor())
    commands_pb2_grpc.add_UserCommandServiceServicer_to_server(
        UserCommandService(), server
    )
    server.add_insecure_port(settings.get_grpc_url())
    # await server.start()
    # await server.wait_for_termination()

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await server.start()
    print("gRPC server started on port 50051")
    
    try:
        await stop_event.wait()  # Ждём сигнала остановки
    finally:
        # Корректное завершение
        await server.stop(5)  # 5 сек на graceful shutdown
        print("Server stopped gracefully")
