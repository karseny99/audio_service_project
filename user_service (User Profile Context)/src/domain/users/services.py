from .models import User
from .value_objects.password_hash import PasswordHash
from .value_objects.email import EmailAddress
from .value_objects.username import Username

from datetime import datetime
from src.core.protos.generated import commands_pb2

class UserRegistrationService:
    """
        Чистая доменная логика без внешних зависимостей

        По сути, валидация данных/сохранение иварианта для агрегата User в этом домене
    """
    
    @classmethod
    def RegisterUser(
        cls,
        email: str,
        raw_password: str,
        username: str
    ) -> User:
        
        email_vo = EmailAddress(email)
        password_hash = PasswordHash(raw_password)
        username_vo = Username(username)
        
        return commands_pb2.RegisterUserResponse(
            user_id=str(5),
            username=username_vo.value,
            email=email_vo.value
        )


        return User(
            email=email_vo,
            password_hash=password_hash,
            username=username_vo
        )


# class UserService:
#     """
#         Registration service
#     """
    
#     def __init__(self, user_repo: UserRepository, event_publisher: EventPublisher):
#         """
#             Initing service with abstract UserRepo implemenation
#         """
#         self.user_repo = user_repo
#         self._publisher = event_publisher

#     async def register_user(
#         self,
#         email: str,
#         hash_password: str,
#         username: str
#     ) -> User:
#         """
#             Register new user, returns User-class if succeed
#         """

#         # object value usage
#         email_vo = EmailAddress(email)
#         password_hash = PasswordHash(hash_password)
#         username = Username(username)

#         if await self.user_repo.get_by_email(email_vo.value):
#             raise ValueError("Email already exists")
        
#         user = User(
#             id=None,
#             email=email_vo,
#             password_hash=password_hash,
#             username=username
#         )
        
#         await self.user_repo.add(user)

#         await self._publisher.publish(
#             UserRegistered(
#                 user_id=user.id,
#                 email=user.email.value,
#                 username=user.username,
#                 occurred_on=datetime.utcnow()
#             )
#         )
#         return user


# class PasswordResetService:
#     """
#         Service of password resetting 
#     """
    
#     def __init__(self, user_repo: UserRepository):
#         self.user_repo = user_repo
#         self.reset_tokens = {}  # Временное хранилище токенов (в продакшене - Redis)

#     async def generate_reset_token(self, user_id: int) -> str:
#         """Генерация токена сброса пароля"""
#         token = str(uuid4())
#         self.reset_tokens[token] = {
#             "user_id": user_id,
#             "expires_at": datetime.utcnow() + timedelta(hours=1)
#         }
#         return token

#     async def reset_password(self, token: str, new_password: str) -> None:
#         """Смена пароля по токену"""
#         if token not in self.reset_tokens:
#             raise ValueError("Неверный токен")
        
#         data = self.reset_tokens[token]
#         if datetime.utcnow() > data["expires_at"]:
#             raise ValueError("Токен истёк")
        
#         user = await self.user_repo.get_by_id(data["user_id"])
#         if not user:
#             raise ValueError("Пользователь не найден")
        
#         user.change_password(PasswordHash.from_raw(new_password))
#         await self.user_repo.update(user)
#         del self.reset_tokens[token]