
# Возможный шаблон

from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    REDIS_PORT: int              
    REDIS_PASSWORD: str           
    REDIS_HOST: str              
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Корневая директория проекта

    # Указание файла с переменными окружения
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")

# Создание экземпляра настроек
settings = Settings()

# Формирование URL для подключения к Redis через SSL

redis_url = f"rediss://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

# Инициализация Кафки
# something here

# Инициализация fastStream
# something here