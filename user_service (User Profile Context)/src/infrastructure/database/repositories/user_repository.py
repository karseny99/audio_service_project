from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.domain.users.repository import UserRepository
from src.domain.users.models import User
from src.core.config import settings
from src.infrastructure.database.models import UserORM
from src.infrastructure.database.repositories.database import ConnectionDecorator


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

    @ConnectionDecorator()
    async def get_by_id(self, user_id: int, session: Optional[AsyncSession] = None) -> Optional[User]:
        user_orm = await session.get(UserORM, user_id)
        return user_orm.to_domain() if user_orm else None

    @ConnectionDecorator()
    async def get_by_email(self, email: str, session: Optional[AsyncSession] = None) -> Optional[User]:
        stmt = select(UserORM).where(UserORM.email == email)
        result = await session.execute(stmt)
        user_orm = result.scalar_one_or_none()
        return user_orm.to_domain() if user_orm else None

    @ConnectionDecorator()
    async def get_by_username(self, username: str, session: Optional[AsyncSession] = None) -> Optional[User]:
        stmt = select(UserORM).where(UserORM.username == username)
        result = await session.execute(stmt)
        user_orm = result.scalar_one_or_none()
        return user_orm.to_domain() if user_orm else None

    @ConnectionDecorator()
    async def add(self, user: User, session: Optional[AsyncSession] = None) -> Optional[User]:
        """Add new user to db"""
        auth_orm = UserORM.from_domain(user)
        session.add(auth_orm)
        await session.flush()       
        return auth_orm.to_domain()

    @ConnectionDecorator()
    async def update(self, user: User, session: Optional[AsyncSession] = None) -> Optional[User]:
        """Update user in db ??????????????????????????????????????????"""
        user_orm = await session.get(UserORM, user.id)
        if not user_orm:
            return None

        user_orm.update_from_domain(user)
        await session.flush()
        return user_orm.to_domain()

    @ConnectionDecorator()
    async def delete(self, user_id: int, session: Optional[AsyncSession] = None) -> bool:
        """
            Deletes user in db
            Return true if success, false otherwise
        """
        user_orm = await session.get(UserORM, user_id)
        if user_orm:
            await session.delete(user_orm)
            return True
        return False
