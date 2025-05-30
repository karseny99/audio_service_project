from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar
import re
import os

class Settings(BaseSettings):
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    ENV: str = "local"  # local/stage/prod
    
    # gRPC server
    GRPC_HOST: str = '[::]' # all interfaces
    GRPC_PORT: str = '50056'

    # Redis
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = '1'
    REDIS_DB: int = 0
    
    # PostgreSQL
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'user'
    POSTGRES_PASSWORD: str = '1'
    POSTGRES_DB: str = 'audio_db'
    
    # Kafka
    EVENT_HEADER: str = 'event-type'
    KAFKA_BOOTSTRAP_SERVERS: str = 'localhost:29092'
    # KAFKA_BOOTSTRAP_SERVERS: str = 'kafka:9092' # in docker network
    KAFKA_USER_CONTEXT_TOPIC: str = 'user-topic'
    KAFKA_PLAYLIST_CONTEXT_TOPIC: str = 'playlist-topic'
    KAFKA_LISTENING_HISTORY_CONTEXT_TOPIC: str = 'listening-history-topic'

    # KAFKA_SECURITY_PROTOCOL: Optional[str] = None
    # KAFKA_SASL_MECHANISM: Optional[str] = None
    # KAFKA_SASL_USERNAME: Optional[str] = None
    # KAFKA_SASL_PASSWORD: Optional[str] = None
    
    # model_config = SettingsConfigDict(
    #     env_file=f"{BASE_DIR}/.env",
    #     env_file_encoding='utf-8',
    #     extra='ignore'
    # )


    # S3
    MINIO_URL: str = "localhost:9000"
    MINIO_USER: str = "admin"
    MINIO_PASSWORD: str = "password"
    MINIO_TRACK_BUCKET: str = "tracks"
    MINIO_TRACK_PATH: str = ""
    MINIO_DEFAULT_CHUNK_SIZE: int = 32768
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    def get_postgres_url(self, async_mode: bool = True) -> str:
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

    def get_grpc_url(self) -> str:
        grpc_url = f"{self.GRPC_HOST}:{self.GRPC_PORT}"
        return grpc_url

settings = Settings()