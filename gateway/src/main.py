# src/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.v1.users import router as users_router
from core.container import Container
from core.kafka_producer import get_producer

container = Container()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Этот контекст запускается один раз при старте и
    завершается при остановке приложения.
    """
    # --- Startup ---
    # Создаём экземпляр продюсера (lazy — создастся при первом get_producer())
    # Можно обернуть в try/except, если нужно пропускать ошибку соединения
    try:
        get_producer()
    except Exception:
        pass

    yield  # здесь приложение начинает обрабатывать запросы

    # --- Shutdown ---
    # Закрываем соединение у продюсера
    try:
        get_producer().close()
    except Exception:
        pass


app = FastAPI(lifespan=lifespan)
app.container = container
app.include_router(users_router)
