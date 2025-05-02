import asyncio
from src.domain.users.services import UserRegistrationService
from src.infrastructure.database.repositories.user_repository \
    import PostgresUserRepository
from src.domain.users.models import User


from concurrent import futures
import grpc
from src.core.protos.generated import commands_pb2
from src.core.protos.generated import commands_pb2_grpc


def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    commands_pb2_grpc.add_UserCommandServiceServicer_to_server(
        UserRegistrationService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()




# async def main():
#     user_repo = PostgresUserRepository()
#     user_service = UserService(user_repo)

#     try:
#         user = await user_service.register_user(
#             email="test@example.com",
#             hash_password="secure123",
#             username="testuser"
#         )
#         print(f"User registered: {user}")
#     except ValueError as e:
#         print(f"Error: {e}")


# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
# from kafka.consumer import app
# from grpc_server import serve_grpc

async def main():
    await asyncio.gather(
        serve_grpc(),  # gRPC-сервер
        # app.run()      # Kafka-консьюмер
    )

asyncio.run(main())