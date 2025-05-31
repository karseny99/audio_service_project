# src/infrastructure/elastic/elastic_repository.py

from typing import Any, Dict, List, Tuple
import asyncio

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_bulk
from src.domain.elastic_search.repository import SearchRepository
from src.core.config import settings
from src.core.logger import logger


class ElasticSearchRepository(SearchRepository):
    """
    Реализация SearchRepository поверх Elasticsearch.
    Жёстко «привязана» к конкретному индексу, название берём из настроек.
    """
    def __init__(self, es_client: AsyncElasticsearch):
        self._client = es_client
        self._index = settings.ELASTIC_TRACK_INDEX  # допустим, "music_tracks"

    async def search(self, body: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int]:
        try:
            result = await self._client.search(
                index=self._index,
                body=body
            )
            hits = result["hits"]["hits"]             # список словарей-«хитов»
            total = result["hits"]["total"]["value"]  # общее число
            return hits, total
        except NotFoundError:
            # Если индекс не найден → вернём 0 результатов
            logger.warning(f"Index {self._index} not found")
            return [], 0
        except Exception as e:
            logger.error(f"Elasticsearch search error: {e}")
            raise


    # Дополнительно (опционально): если нужна массовая загрузка/обновление:
    async def bulk_index(self, actions: List[Dict[str, Any]]) -> None:
        """
        Примерная реализация массовой индексации через helpers.async_bulk.
        `actions` — список dict с полями: {'_index': ..., '_id': ..., '_source': {...}}.
        """
        try:
            await async_bulk(
                client=self._client,
                actions=actions,
                index=self._index
            )
        except Exception as e:
            logger.error(f"Elasticsearch bulk index error: {e}")
            raise
