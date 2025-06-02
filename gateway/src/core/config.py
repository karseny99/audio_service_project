from pydantic_settings import BaseSettings
import os
import logging
import re
from typing import ClassVar

class Settings(BaseSettings):

    BCRYPT_SALT: ClassVar[str] = "$2b$12$ABCDEFGHIJKLMNOPQRSTUV"

    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    ENV: str = "local"  # local/stage/prod


    # Logger
    LOG_LEVEL: int = logging.DEBUG # INFO
    LOKI_URL: str = "http://loki:3100"
    
    
    # gRPC
    GRPC_HOST: str = 'localhost' # all interfaces
    GRPC_PORT: str = '50051'

    MUSIC_CATALOG_GRPC_URL: str = "localhost:50053"
    LISTENING_HISTORY_GRPC_URL: str = "localhost:50054"
    STREAMING_SERVICE_GRPC_URL: str = 'localhost:50056'
    TRACK_SEARCH_GRPC_URL: str = "localhost:50054"  
    
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
        """
            Returns grpc url 
        """
        grpc_url = f"{self.GRPC_HOST}:{self.GRPC_PORT}"
        return grpc_url

settings = Settings()