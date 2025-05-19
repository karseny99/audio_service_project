from src.domain.events.events import UserRegistered, UserDeleted
from src.domain.users.repository import UserRepository
from src.domain.users.services import UserRegistrationService
from src.domain.events.publisher import EventPublisher
from src.core.exceptions import EmailAlreadyExistsError, UsernameAlreadyExistsError
from src.core.logger import logger

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

    async def execute(self, email: str, password: str, username: str) -> int:
        if await self._repo.get_by_email(email=email):
            logger.debug(f"{email} exists")
            raise EmailAlreadyExistsError("Email exists")
        if await self._repo.get_by_username(username=username):
            logger.debug(f"{username} exists")
            raise UsernameAlreadyExistsError("Username exists")
        
        user = self._service.register_user(
            email=email, 
            password=password, 
            username=username
        )
        
        user = await self._repo.add(user=user)
        logger.info(f"Registered: {user}")


        # await self._publisher.publish(
        #     event=UserDeleted(
        #         user_id=str(user.id),
        #     ),
        #     key=str(user.id)
        # )

        return str(user.id)