import grpc

from user_context.generated import commands_pb2
from user_context.generated import commands_pb2_grpc

def register_user(username: str, email: str, password: str) -> str:
    """
    Регистрирует пользователя через gRPC
    
    Args:
        username: Имя пользователя
        email: Email
        password: Пароль
        
    Returns:
        str: ID созданного пользователя
        
    Raises:
        grpc.RpcError: В случае ошибки gRPC
        ValueError: Если не пройдена валидация на сервере
    """
    # 1. Создаем канал (в продакшене должен быть singleton)
    with grpc.insecure_channel(
        'localhost:50051',
        options=[
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.enable_retries', 1)
        ]
    ) as channel:
        # 2. Инициализируем stub
        stub = commands_pb2_grpc.UserCommandServiceStub(channel)
        
        # 3. Формируем запрос
        request = commands_pb2.RegisterUserRequest(
            username=str(username),
            email=str(email),
            password=str(password)
        )
        
        try:
            # 4. Выполняем вызов с таймаутом
            response = stub.RegisterUser(request, timeout=10.0)
            return str(response.user_id)
            
        except grpc.RpcError as e:
            # Обработка специфичных ошибок
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise ValueError(f"Validation error: {e.details()}")
            elif e.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise ValueError("User already exists")
            else:
                raise RuntimeError(f"gRPC error [{e.code()}]: {e.details()}")
