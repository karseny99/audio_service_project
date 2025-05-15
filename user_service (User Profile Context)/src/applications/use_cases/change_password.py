# user_service/src/applications/use_cases/change_password.py

from datetime import datetime
from src.domain.users.value_objects.password_hash import PasswordHash
from src.domain.events.events import PasswordChangedEvent
from src.domain.events.publisher import EventPublisher
from src.domain.users.repository import UserRepository
from src.core.exceptions import UserNotFoundError, InvalidPasswordError

class ChangePasswordUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        event_publisher: EventPublisher
    ):
        self._repo = user_repo
        self._publisher = event_publisher

    async def execute(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> None:
        # 1. Получаем агрегат
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        # 2. Проверяем старый пароль
        if not user.password_hash.verify(old_password):
            raise InvalidPasswordError("Old password incorrect")

        # 3. Устанавливаем новый хэш
        new_hash = PasswordHash(new_password)  # сам хэширует
        user.change_password(new_hash)

        # 4. Сохраняем
        await self._repo.update(user)

        # 5. (опционально) публикуем событие
        await self._publisher.publish(
            event=PasswordChangedEvent(
                user_id=str(user.id),
                changed_at=datetime.utcnow()
            ),
            topic=self._publisher.destination,
            key=str(user.id)
        )
