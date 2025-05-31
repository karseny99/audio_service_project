from elasticsearch import AsyncElasticsearch
from src.core.config import settings
from src.core.logger import logger


class ElasticClient:
    """
    Singleton-обёртка над AsyncElasticsearch.
    Для подключения используем URL из настроек.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
        return cls._instance

    async def connect(self):
        if self._client is None:
            self._client = AsyncElasticsearch(
                hosts=[settings.ELASTIC_HOST],
                http_auth=(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD) if settings.ELASTIC_USER else None,
                timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
            logger.info(f"Connected to Elasticsearch at {settings.ELASTIC_HOST}")

    async def disconnect(self):
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> AsyncElasticsearch:
        if self._client is None:
            raise RuntimeError("Elasticsearch client not connected")
        return self._client
