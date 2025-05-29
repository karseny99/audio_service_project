
from datetime import datetime, date
from typing import Type, Optional, Any
import json 

from src.domain.cache.serialization import CacheSerializer
from src.domain.users.models import User
from src.domain.users.value_objects.email import EmailAddress
from src.domain.users.value_objects.password_hash import PasswordHash
from src.domain.users.value_objects.username import Username

from src.core.exceptions import ValueObjectException
from src.core.logger import logger

class UserSerializer(CacheSerializer):
    def __init__(self, base_serializer: CacheSerializer):
        self._base = base_serializer

    def serialize(self, user: Optional['User']) -> bytes:
        if user is None:
            return self._base.serialize(None)
        
        # Преобразуем User в словарь
        user_dict = {
            'user_id': user.id,
            'email': user.email.value,  # Извлекаем значение value object
            'username': user.username.value,
            'password_hash': user.password_hash.value,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
        return self._base.serialize(user_dict)

    def deserialize(self, data: bytes, target_type: Type[Optional['User']]) -> Optional['User']:
        if data is None:
            return None
            
        decoded = self._base.deserialize(data, dict)
        
        if decoded is None:
            return None
            
        try:
            # Создаем value objects
            email = EmailAddress(decoded['email'])
            username = Username(decoded['username'])
            password_hash = PasswordHash(decoded['password_hash'])
            
            # Создаем пользователя
            return target_type(
                id=int(decoded['id']),
                email=email,
                username=username,
                password_hash=password_hash,
                created_at=datetime.fromisoformat(decoded['created_at']) if decoded['created_at'] else None
            )
        except (ValueObjectException, KeyError, ValueError) as e:
            logger.error(f"Failed to deserialize user: {e}")
            return None


class SimpleSerializer(CacheSerializer):
    def __init__(self, base_serializer: CacheSerializer):
        self._base = base_serializer

    def serialize(self, obj: Any) -> bytes:
        if obj is None:
            return b'null'

        if isinstance(obj, (int, float, str, bool)):
            return json.dumps(obj).encode('utf-8')

        raise ValueError(f"Unsupported type for serialization: {type(obj)}")


    def deserialize(self, data: bytes, target_type: Type) -> Any:
        if data == b'null':
            return None
        
        decoded = json.loads(data.decode('utf-8'))
        
        if target_type in (int, float, str, bool, type(None)):
            return decoded

        raise ValueError(f"Unsupported target type: {target_type}")