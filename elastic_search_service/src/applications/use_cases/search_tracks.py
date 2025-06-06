from typing import List, Any, Dict

from src.domain.elastic_search.repository import SearchRepository
from src.domain.cache.cache_repository import CacheRepository, CacheTTL
from src.domain.cache.serialization import CacheSerializer
from src.core.exceptions import DomainError
from src.applications.decorators.cache import cached

from src.applications.models import ElasticTrackRequest, ElasticTrackResponse, TrackItem


class SearchTracksUseCase:
    """
    Use case для поиска треков в Elasticsearch.
    Получает ElasticTrackRequest, валидирует, формирует DSL-запрос к ES, 
    вызывает SearchRepository и возвращает ElasticTrackResponse.
    """
    def __init__(self, search_repo: SearchRepository, _cache_repo, _cache_serializer):
        self._search_repo = search_repo
        self._cache_repo = _cache_repo
        self._cache_serializer = _cache_serializer

    @cached(
        key_template="search:title={title}:artist={artist_name}:genres={genre_name}:"
                    "min_dur={min_duration_ms}:max_dur={max_duration_ms}:"
                    "explicit={explicit}:from={release_date_from}:to={release_date_to}:"
                    "page={page}:size={page_size}",
        ttl=CacheTTL.DEFAULT
    )
    async def execute(self, request: ElasticTrackRequest) -> ElasticTrackResponse:
        # хотя бы одно поле фильтрации должно быть непустым
        has_any_filter = any([
            request.title, 
            request.artist_name, 
            request.genre_name,
            request.min_duration_ms, 
            request.max_duration_ms,
            request.explicit is not None,
            request.release_date_from,
            request.release_date_to
        ])
        if not has_any_filter:
            raise DomainError("Нужно хотя бы одно условие фильтрации")

        must_clauses: List[Dict[str, Any]] = []
        if request.title:
            must_clauses.append({
                "match": {"title": {"query": request.title, "fuzziness": "AUTO"}}
            })
        if request.artist_name:
            must_clauses.append({
                "match": {
                    "artists": {
                        "query": request.artist_name,
                        "fuzziness": "AUTO"
                    }
                }
            })
        if request.genre_name:
            must_clauses.append({
                "terms": {
                    "genres": request.genre_name
                }
            })
        if request.min_duration_ms is not None or request.max_duration_ms is not None:
            range_body: Dict[str, Any] = {}
            if request.min_duration_ms is not None:
                range_body["gte"] = request.min_duration_ms
            if request.max_duration_ms is not None:
                range_body["lte"] = request.max_duration_ms
            must_clauses.append({
                "range": {"duration_ms": range_body}
            })
        if request.explicit is not None:
            must_clauses.append({
                "term": {"explicit": request.explicit}
            })
        if request.release_date_from or request.release_date_to:
            range_date: Dict[str, Any] = {}
            if request.release_date_from:
                range_date["gte"] = request.release_date_from.isoformat()
            if request.release_date_to:
                range_date["lte"] = request.release_date_to.isoformat()
            must_clauses.append({
                "range": {"release_date": range_date}
            })

        # Если вдруг нет ни одного «must», это бы отфильтровалось выше, но на всякий случай:
        if not must_clauses:
            raise DomainError("Не удалось сформировать условия поиска")

        es_query: Dict[str, Any] = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            },
            "from": ((request.page - 1) * request.page_size),
            "size": request.page_size
        }
        hits, total = await self._search_repo.search(es_query)

        track_items: List[TrackItem] = []
        for doc in hits:
            # Ожидаем, что репозиторий вернёт Python-dict с уже распаршенным полем "_source"
            src: Dict[str, Any] = doc["_source"]
            item = TrackItem(
                track_id=src.get("track_id"),
                title=src.get("title"),
                duration_ms=src.get("duration_ms"),
                artists=src.get("artists"),
                genres=src.get("genres"),
                explicit=src.get("explicit"),
                release_date=src.get("release_date")
            )
            track_items.append(item)

        response = ElasticTrackResponse(
            tracks=track_items,
            total=total,
            page=request.page,
            page_size=request.page_size,
            success=True
        )
        return response
