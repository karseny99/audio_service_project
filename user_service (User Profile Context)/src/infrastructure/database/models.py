from datetime import datetime
from sqlalchemy import BigInteger, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List

from src.domain.users.models import User as DomainUser
from src.domain.users.value_objects.email import EmailAddress
from src.domain.users.value_objects.password_hash import PasswordHash
from src.domain.users.value_objects.username import Username

class Base(DeclarativeBase):
    pass

# User Profile Context
class UserORM(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user_profile"}

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    audit_logs: Mapped[List["UserAuditLogORM"]] = relationship(back_populates="user")

    @classmethod
    def from_domain(cls, user: DomainUser) -> "UserORM":
        return cls(
            username=user.username.value,
            email=user.email.value,
            password_hash=user.password_hash.value,
            created_at=user.created_at
        )

    def to_domain(self) -> DomainUser:
        return DomainUser(
            id=self.user_id,
            email=EmailAddress(self.email),
            username=Username(self.username),
            password_hash=PasswordHash(self.password_hash),
            created_at=self.created_at
        )

class UserAuditLogORM(Base):
    __tablename__ = "user_audit_log"
    __table_args__ = {"schema": "user_profile"}

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_profile.users.user_id"))
    field_name: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
    changed_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["UserORM"] = relationship(back_populates="audit_logs")


# old version alchemy 1.*
# class UserORM(Base):
#     """
#         SQLAlchemy user's model
#     """
#     __tablename__ = "users"
#     __table_args__ = {'schema': 'user_profile'}

#     user_id = Column(BigInteger, primary_key=True, autoincrement=True)
#     username = Column(String(255), unique=True, nullable=False)
#     email = Column(String(255), unique=True, nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     password_hash = Column(Text, nullable=False)

#     @classmethod
#     def from_domain(cls, user: DomainUser) -> "UserORM":
#         """
#             Convert domain to alchemy
#         """
#         return cls(
#             username=user.username.value,
#             email=user.email.value,
#             created_at=user.created_at,
#             password_hash=user.password_hash.value,
#         )

#     def to_domain(self) -> DomainUser:
#         """
#             Convert alchemy to domain
#         """
#         return DomainUser(
#             id=self.user_id,
#             email=EmailAddress(self.email),
#             username=Username(self.username),
#             password_hash=PasswordHash(self.password_hash),
#             created_at=self.created_at
#         )

#     def update_from_domain(self, user: DomainUser) -> None:
#         """
#             Update model with domain data
#         """
#         self.user_id = user.id
#         self.email = user.email.value
#         self.username = user.username.value
#         self.created_at = user.created_at
#         self.password_hash = user.password_hash.value