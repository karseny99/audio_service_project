from sqlalchemy import Column, String, DateTime, func, BigInteger, Text
from sqlalchemy.orm import declarative_base
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

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    password_hash = Column(Text, nullable=False)

    @classmethod
    def from_domain(cls, user: DomainUser) -> "UserORM":
        """
            Convert domain to alchemy
        """
        return cls(
            username=user.username.value,
            email=user.email.value,
            created_at=user.created_at,
            password_hash=user.password_hash.value,
        )

    def to_domain(self) -> DomainUser:
        """
            Convert alchemy to domain
        """
        return DomainUser(
            id=self.user_id,
            email=EmailAddress(self.email),
            username=Username(self.username),
            password_hash=PasswordHash(self.password_hash),
            created_at=self.created_at
        )

    def update_from_domain(self, user: DomainUser) -> None:
        """
            Update model with domain data
        """
        self.user_id = user.id
        self.email = user.email.value
        self.username = user.username.value
        created_at = user.created_at
        self.password_hash = user.password_hash.value