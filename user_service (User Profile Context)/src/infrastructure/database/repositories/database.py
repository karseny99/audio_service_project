from functools import wraps
from typing import Optional, Callable, Any
from sqlalchemy import text

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