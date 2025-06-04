from src.domain.events.events import UserRegistered, UserDeleted
from src.domain.users.repository import UserRepository
from src.domain.users.services import UserRegistrationService
from src.domain.events.publisher import EventPublisher
from src.core.exceptions import EmailAlreadyExistsError, UsernameAlreadyExistsError
from src.core.logger import logger

class DeleteUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        event_publisher: EventPublisher,
    ):
        self._repo = user_repo
        self._publisher = event_publisher

    async def execute(self, user_id: int) -> bool:
        
        isDeleted = await self._repo.delete(user_id)
        logger.info(f"Deleted: {user_id}")

        await self._publisher.publish(
            event=UserDeleted(
                user_id=str(user_id),
            ),
            key=str(user_id)
        )

        return isDeleted