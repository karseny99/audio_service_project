
from sqlalchemy.orm import async_sessionmaker
from sqlalchemy import create_async_engine
from app.config import settings

DATABASE_URL = settings.get_db_url()

# Создаем асинхронный движок для работы с базой данных
engine = create_async_engine(url=DATABASE_URL)

# Создаем фабрику сессий для взаимодействия с базой данных
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                # Явно не открываем транзакции, так как они уже есть в контексте
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()  # Откатываем сессию при ошибке
                raise e  # Поднимаем исключение дальше
            finally:
                await session.close()  # Закрываем сессию

    return wrapper



'''
Либо 

from functools import wraps
from typing import Optional
from sqlalchemy import text
from dao.database import async_session_maker

def connection(self, isolation_level: Optional[str] = None, commit: bool = True):
    """
    Декоратор для управления сессией с возможностью настройки уровня изоляции и коммита.
    Параметры:
    - `isolation_level`: уровень изоляции для транзакции (например, "SERIALIZABLE").
    - `commit`: если `True`, выполняется коммит после вызова метода.
    """
    def decorator(method):
        @wraps(method)
        async def wrapper(*args, **kwargs):
            async with self.session_maker() as session:
                try:
                    if isolation_level:
                        await session.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"))
                    result = await method(*args, session=session, **kwargs)
                    if commit:
                        await session.commit()
                    return result
                except Exception as e:
                    await session.rollback()
                    raise
                finally:
                    await session.close()
        return wrapper
    return decorator

'''