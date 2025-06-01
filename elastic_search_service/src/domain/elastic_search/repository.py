# src/domain/music_search/repository.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class SearchRepository(ABC):
    @abstractmethod
    async def search(self, body: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int]:
        """
        Выполняет запрос в Elasticsearch.
        `body` — это полный DSL-запрос (python dict).
        Возвращает:
          - список документов (каждый документ — словарь, отражающий полный ответ ES, 
            как правило, [{"_source": {…}, "_id": "...", ...}, …])
          - общее число найденных записей (тот же total по ES response)
        """
        raise NotImplementedError
