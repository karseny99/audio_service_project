import grpc

from user_context.generated import commands_pb2
from user_context.generated import commands_pb2_grpc

def register_user(username: str, email: str, password: str) -> str:
    # 1. Создаем канал (рекомендуется singleton в реальном коде)
    channel = grpc.insecure_channel('user-service:50051')
    
    # 2. Инициализируем stub
    stub = commands_pb2_grpc.UserCommandServiceStub(channel)
    
    # 3. Формируем запрос
    request = commands_pb2.RegisterUserRequest(
        username=username,
        email=email,
        password=password
    )
    
    try:
        # 4. Выполняем RPC-вызов
        response = stub.RegisterUser(request)
        return response.user_id
        
    except grpc.RpcError as e:
        # Обработка ошибок gRPC
        print(f"Error [{e.code()}]: {e.details()}")
        raise

