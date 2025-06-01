from elasticsearch import AsyncElasticsearch
from src.core.config import settings
from src.core.logger import logger


class ElasticClient:
    """
    Обёртка над AsyncElasticsearch.
    """
    def __init__(self):
        self._client = None  # Будет создан при подключении

    async def connect(self):
        if self._client is None:
            self._client = AsyncElasticsearch(
                hosts=[settings.ELASTIC_HOST],
                http_auth=(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD) if settings.ELASTIC_USER else None,
                timeout=30,
                max_retries=3,
                retry_on_timeout=True,
                verify_certs=False,
                ssl_show_warn=False
            )
            try:
                info = await self._client.info()
                logger.info(f"Connected to Elasticsearch at {settings.ELASTIC_HOST}")
                logger.debug(f"Elasticsearch info: {info}")
            except Exception as e:
                logger.error(f"Elasticsearch connection error: {str(e)}")
                raise

    async def disconnect(self):
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> AsyncElasticsearch:
        if self._client is None:
            raise RuntimeError("Elasticsearch client not connected")
        return self._client