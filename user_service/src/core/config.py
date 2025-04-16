from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from typing import Optional

class Settings(BaseSettings):
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    ENV: str = "local"  # local/stage/prod
    
    # Redis
    # REDIS_HOST: str
    # REDIS_PORT: int
    # REDIS_PASSWORD: str
    # REDIS_DB: int = 0
    
    # PostgreSQL
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'password'
    POSTGRES_PASSWORD: str = 'password'
    POSTGRES_DB: str = 'audio'
    
    # Kafka
    # KAFKA_BOOTSTRAP_SERVERS: str
    # KAFKA_SECURITY_PROTOCOL: Optional[str] = None
    # KAFKA_SASL_MECHANISM: Optional[str] = None
    # KAFKA_SASL_USERNAME: Optional[str] = None
    # KAFKA_SASL_PASSWORD: Optional[str] = None
    
    # model_config = SettingsConfigDict(
    #     env_file=f"{BASE_DIR}/.env",
    #     env_file_encoding='utf-8',
    #     extra='ignore'
    # )
    
    def get_redis_url(self, use_ssl: bool = True) -> str:
        """
            Returns redis url 
        """
        scheme = "rediss" if use_ssl else "redis"
        return f"{scheme}://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def get_postgres_url(self, async_mode: bool = True) -> str:
        """
            Returns psql url 
        """
        driver = "postgresql+asyncpg" if async_mode else "postgresql"
        return f"{driver}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    def get_kafka_config(self) -> dict:
        """
            Returns kafka config 
        """
        config = {
            "bootstrap_servers": self.KAFKA_BOOTSTRAP_SERVERS
        }
        if self.KAFKA_SECURITY_PROTOCOL:
            config.update({
                "security_protocol": self.KAFKA_SECURITY_PROTOCOL,
                "sasl_mechanism": self.KAFKA_SASL_MECHANISM,
                "sasl_plain_username": self.KAFKA_SASL_USERNAME,
                "sasl_plain_password": self.KAFKA_SASL_PASSWORD
            })
        return config

settings = Settings()