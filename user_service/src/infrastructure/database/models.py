from sqlalchemy import Column, String, UUID, DateTime, func
from sqlalchemy.orm import declarative_base
from uuid import uuid4
from src.domain.users.models import User as DomainUser
from src.domain.users.value_objects.email import EmailAddress
from src.domain.users.value_objects.password_hash import PasswordHash
from src.domain.users.value_objects.username import Username

Base = declarative_base()

class UserORM(Base):
    """
        SQLAlchemy user's model
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    def from_domain(cls, user: DomainUser) -> "UserORM":
        """
            Convert domain to alchemy
        """
        return cls(
            id=user.id,
            email=user.email.value,  # Извлекаем значение из VO
            username=user.username.value,
            password_hash=user.password_hash.value
        )

    def to_domain(self) -> DomainUser:
        """
            Convert alchemy to domain
        """
        return DomainUser(
            id=self.id,
            email=EmailAddress(self.email),
            username=Username(self.username),
            password_hash=PasswordHash(self.password_hash),
            created_at=self.created_at
        )

    def update_from_domain(self, user: DomainUser) -> None:
        """
            Update model with domain data
        """
        self.email = user.email.value
        self.username = user.username.value
        self.password_hash = user.password_hash.value