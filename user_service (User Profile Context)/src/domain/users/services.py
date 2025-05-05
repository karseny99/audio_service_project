from src.domain.users.models import User
from src.domain.users.value_objects.password_hash import PasswordHash
from src.domain.users.value_objects.email import EmailAddress
from src.domain.users.value_objects.username import Username

class UserRegistrationService:
    """
        Чистая доменная логика без внешних зависимостей

        По сути, валидация данных/сохранение иварианта для агрегата User в этом домене
    """
    
    @classmethod
    def register_user(
        cls,
        email: str,
        username: str,
        password: str,
    ) -> User:
        
        email_vo = EmailAddress(email)
        password_hash = PasswordHash(password)
        username_vo = Username(username)

        return User(
            id=None,
            email=email_vo,
            password_hash=password_hash,
            username=username_vo
        )