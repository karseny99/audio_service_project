from functools import wraps
from typing import Optional, Callable, Any
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.domain.users.repository import UserRepository
from src.domain.users.models import User
from src.core.config import settings
from src.infrastructure.database.models import UserORM
from uuid import UUID


class ConnectionDecorator:
    """
        SingleTone decorator
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConnectionDecorator, cls).__new__(cls)
        return cls._instance

    def __init__(self, isolation_level: Optional[str] = None, commit: bool = True):
        self.isolation_level = isolation_level
        self.commit = commit

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            self_instance = args[0]  # Get the instance
            async with self_instance.session_maker() as session:
                try:
                    if self.isolation_level:
                        await session.execute(
                            text(f"SET TRANSACTION ISOLATION LEVEL {self.isolation_level}")
                        )
                    result = await func(*args, session=session, **kwargs)
                    if self.commit:
                        await session.commit()
                    return result
                except Exception as e:
                    await session.rollback()
                    raise
        return wrapper


class PostgresUserRepository(UserRepository):
    def __init__(self):
        self.engine = create_async_engine(
            url=settings.get_postgres_url(),
            echo=False 
        )
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False
        )

    @ConnectionDecorator(isolation_level="READ COMMITTED")
    async def get_by_id(self, user_id: UUID, session: Optional[AsyncSession] = None) -> Optional[User]:
        user_orm = await session.get(UserORM, user_id)
        return user_orm.to_domain() if user_orm else None
    
    @ConnectionDecorator(isolation_level="READ COMMITTED")
    async def get_by_email(self, email: str, session: Optional[AsyncSession] = None) -> Optional[User]:
            stmt = select(UserORM).where(UserORM.email == email)
            result = await session.execute(stmt)
            user_orm = result.scalar_one_or_none()
            return user_orm.to_domain() if user_orm else None


    @ConnectionDecorator()
    async def add(self, user: User, session: Optional[AsyncSession] = None) -> None:
        """Add new user to db"""
        user_orm = UserORM.from_domain(user)
        session.add(user_orm)

    @ConnectionDecorator()
    async def update(self, user: User, session: Optional[AsyncSession] = None) -> None:
        """Update user in db"""
        user_orm = await session.get(UserORM, user.id)
        if user_orm:
            user_orm.update_from_domain(user)

    @ConnectionDecorator()
    async def delete(self, user_id: UUID, session: Optional[AsyncSession] = None) -> bool:
        """Delete user in db"""
        user_orm = await session.get(UserORM, user_id)
        if user_orm:
            await session.delete(user_orm)
            return True
        return False
