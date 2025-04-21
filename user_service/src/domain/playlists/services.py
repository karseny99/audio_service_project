from src.infrastructure.kafka.producers import EventPublisher
from src.domain.events.events import UserRegistered
from .models import User
from .value_objects.password_hash import PasswordHash
from .value_objects.email import EmailAddress
from .value_objects.username import Username
from .repository import PlaylistRepository

from datetime import datetime

class PlaylistService:   
    def __init__(self, user_repo: PlaylistRepository, event_publisher: EventPublisher):
        """
            Initing service with abstract UserRepo implemenation and event publisher
        """
        self.user_repo = user_repo
        self._publisher = event_publisher

    async def register_user(
        self,
        email: str,
        hash_password: str,
        username: str
    ) -> User:
        """
            Register new user, returns User-class if succeed
        """

        # object value usage
        email_vo = EmailAddress(email)
        password_hash = PasswordHash(hash_password)
        username = Username(username)

        if await self.user_repo.get_by_email(email_vo.value):
            raise ValueError("Email already exists")
        
        user = User(
            id=None,
            email=email_vo,
            password_hash=password_hash,
            username=username
        )
        
        await self.user_repo.add(user)

        await self._publisher.publish(
            UserRegistered(
                user_id=user.id,
                email=user.email.value,
                username=user.username,
                occurred_on=datetime.utcnow()
            )
        )
        return user
