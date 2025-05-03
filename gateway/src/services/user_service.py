# gateway/services/user_service.py
from grpc import RpcError, StatusCode
from src.core.dependencies.grpc_clients import get_user_channel
from src.protos.user_context.generated import commands_pb2, commands_pb2_grpc

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
        ValueError: Если не пройдена валидация или пользователь существует
        RuntimeError: Для всех остальных ошибок gRPC
    """
    # 1. Получаем singleton-канал
    channel = get_user_channel()
    
    # 2. Инициализируем stub (создаётся при каждом вызове - это дёшево)
    stub = commands_pb2_grpc.UserCommandServiceStub(channel)
    
    # 3. Формируем запрос
    request = commands_pb2.RegisterUserRequest(
        username=str(username),
        email=str(email),
        password=str(password)
    )
    
    try:
        # 4. Выполняем вызов
        response = stub.RegisterUser(request, timeout=10.0)
        return str(response.user_id)
        
    except RpcError as e:
        if e.code() == StatusCode.INVALID_ARGUMENT:
            raise ValueError(f"Ошибка валидации: {e.details()}")
        elif e.code() == StatusCode.ALREADY_EXISTS:
            raise ValueError("Пользователь уже существует")
        elif e.code() == StatusCode.UNAVAILABLE:
            raise RuntimeError("Сервис пользователей недоступен")
        else:
            raise RuntimeError(f"Ошибка gRPC: {e.code().name}")