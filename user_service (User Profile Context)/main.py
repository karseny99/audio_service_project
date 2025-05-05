from src.infrastructure.grpc.server import serve_grpc



# import asyncio
# from src.applications.use_cases.register_user import RegisterUserUseCase
# from src.infrastructure.database.repositories.user_repository import PostgresUserRepository
# from src.domain.users.services import UserRegistrationService
# import random 
# async def main():

#     register_use_case = RegisterUserUseCase(
#         user_repo=PostgresUserRepository(),
#         # event_publisher=Kafka(),
#         registration_service=UserRegistrationService
#     )

#     request = [f"email@email.com{random.randint(1, 10**10)}", "fdalkfdsajlkfdsa", f"{random.randint(1, 10**10)}"]

#     user_id = await register_use_case.execute(
#         email=request[0],
#         password=request[1],
#         username=request[2]
#     )

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

asyncio.run(serve_grpc())