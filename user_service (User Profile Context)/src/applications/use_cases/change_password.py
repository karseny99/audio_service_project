from datetime import datetime
from src.domain.users.value_objects.password_hash import PasswordHash
from src.domain.events.publisher import EventPublisher
from src.domain.users.repository import UserRepository
from src.core.exceptions import UserNotFoundError, InvalidPasswordError

class ChangePasswordUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        # event_publisher: EventPublisher
    ):
        self._repo = user_repo
        # self._publisher = event_publisher

    async def execute(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> None:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        if user.password_hash.value != old_password:
            raise InvalidPasswordError("Old password incorrect")

        user.change_password(PasswordHash(new_password))
        await self._repo.update(user)

        # Опциональная публикация события
        # await self._publisher.publish(...)