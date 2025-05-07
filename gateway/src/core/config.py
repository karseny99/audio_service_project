import os
import logging
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    ENV: str = "local"                # local / stage / prod

    # Logger
    LOG_LEVEL: int = logging.DEBUG    # или logging.INFO в проде
    LOKI_URL: str = "http://loki:3100"

    # gRPC
    GRPC_HOST: str = 'localhost'
    GRPC_PORT: int = 50051

    # Kafka (дефолт на localhost:9092)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_SECURITY_PROTOCOL: Optional[str] = None
    KAFKA_SASL_MECHANISM: Optional[str] = None
    KAFKA_SASL_USERNAME: Optional[str] = None
    KAFKA_SASL_PASSWORD: Optional[str] = None

    class Config:
        env_file = None
        extra = "ignore"

    def get_grpc_url(self) -> str:
        return f"{self.GRPC_HOST}:{self.GRPC_PORT}"

    def get_kafka_config(self) -> dict:
        cfg = { "bootstrap_servers": self.KAFKA_BOOTSTRAP_SERVERS }
        if self.KAFKA_SECURITY_PROTOCOL:
            cfg.update({
                "security_protocol": self.KAFKA_SECURITY_PROTOCOL,
                "sasl_mechanism": self.KAFKA_SASL_MECHANISM,
                "sasl_plain_username": self.KAFKA_SASL_USERNAME,
                "sasl_plain_password": self.KAFKA_SASL_PASSWORD,
            })
        return cfg

# Создаём единственный экземпляр
settings = Settings()
