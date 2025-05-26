# gateway/services/user_service.py
import sys
from grpc import RpcError, StatusCode
from src.core.dependencies.grpc_clients import get_user_command_stub
from src.protos.user_context.generated import commands_pb2, commands_pb2_grpc
from src.core.password_utils import hash_password


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
    stub = get_user_command_stub()
    
    # 3. Формируем запрос
    hashed_password = hash_password(password)
    request = commands_pb2.RegisterUserRequest(
        username=str(username),
        email=str(email),
        password=hashed_password
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


def authenticate_user(username: str, password: str) -> str:
    """
    Аутентификация пользователя через gRPC

    Returns:
        str: user_id

    Raises:
        ValueError: если неверные креды или пользователь не найден
        RuntimeError: все остальные ошибки
    """
    stub = get_user_command_stub()

    hashed_password = hash_password(password)

    request = commands_pb2.AuthenticateUserRequest(
        username=username,
        password=hashed_password
    )
    try:
        response = stub.AuthenticateUser(request, timeout=5.0)
        return str(response.user_id)
    except RpcError as e:
        if e.code() == StatusCode.NOT_FOUND:
            raise ValueError("Пользователь не найден")
        elif e.code() == StatusCode.INVALID_ARGUMENT:
            raise ValueError("Неверные учетные данные")
        elif e.code() == StatusCode.UNAVAILABLE:
            raise RuntimeError("Сервис пользователей недоступен")
        else:
            raise RuntimeError(f"Ошибка gRPC: {e.code().name}")

def change_password(user_id: str, old_password: str, new_password: str) -> None:
    """
    Меняет пароль пользователя через gRPC.
    Raises:
      ValueError: если неверные креды
      RuntimeError: при прочих ошибках
    """

    old_password_hashed = hash_password(old_password)
    new_password_hashed = hash_password(new_password)

    stub = get_user_command_stub()
    request = commands_pb2.ChangePasswordRequest(
        user_id=user_id,
        old_password=old_password_hashed,
        new_password=new_password_hashed
    )
    try:
        stub.ChangePassword(request, timeout=5.0)
    except RpcError as e:
        code = e.code()
        if code == StatusCode.INVALID_ARGUMENT:
            raise ValueError(f"Ошибка валидации: {e.details()}")
        elif code == StatusCode.NOT_FOUND:
            raise ValueError("Пользователь не найден")
        elif code == StatusCode.UNAVAILABLE:
            raise RuntimeError("Сервис пользователей недоступен")
        else:
            raise RuntimeError(f"Ошибка gRPC: {code.name}")

def get_user_info(user_id: int) -> None:
    """
    Получает информацию о пользователе через gRPC.
    Raises:
      ValueError: если неверные креды
      RuntimeError: при прочих ошибках
    """


    stub = get_user_command_stub()
    request = commands_pb2.GetUserInfoRequest(
        user_id=user_id
    )
    try:
        stub.GetUserInfo(request, timeout=5.0)
    except RpcError as e:
        code = e.code()
        if code == StatusCode.INVALID_ARGUMENT:
            raise ValueError(f"Ошибка валидации: {e.details()}")
        elif code == StatusCode.NOT_FOUND:
            raise ValueError("Пользователь не найден")
        elif code == StatusCode.UNAVAILABLE:
            raise RuntimeError("Сервис пользователей недоступен")
        else:
            raise RuntimeError(f"Ошибка gRPC: {code.name}")