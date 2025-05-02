from src.domain.events.events import UserRegistered
from src.domain.users.repository import UserRepository
from src.domain.users.services import UserRegistrationService
from src.domain.users.models import User

from src.core.exceptions import EmailAlreadyExistsError 

class RegisterUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        event_publisher: EventPublisher,
        registration_service: UserRegistrationService
    ):
        self._repo = user_repo
        self._publisher = event_publisher
        self._service = registration_service

    async def execute(self, email: str, password: str, username: str) -> User:
        # Инфраструктурная операция
        if await self._repo.exists_by_email(email):
            raise EmailAlreadyExistsError("Email exists")
        
        # Бизнес логика (останется такой же при замене бд, например)
        user = self._service.register_user(email, password, username)
        
        # Инфраструктурные операции
        await self._repo.add(user) # Добавление в репу
        await self._publisher.publish(
            UserRegistered(user_id=user.id, ...)   # Паблиш события в очередь, чтоб другой сервис/контекст подхватил
        )
        
        return user