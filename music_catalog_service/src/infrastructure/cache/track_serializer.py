from functools import singledispatchmethod
from typing import Any, Optional
from datetime import datetime, date

from src.domain.cache.serialization import CacheSerializer
from src.domain.music_catalog.models import Track, ArtistInfo, Genre, DurationMs

class TrackSerializer(CacheSerializer):
    def __init__(self, base_serializer: CacheSerializer):
        self._base = base_serializer

    @singledispatchmethod
    def serialize(self, obj: Any) -> bytes:
        return self._base.serialize(obj)

    @serialize.register       # будет срабатывать на экземпляры Track
    def _(self, track: Track) -> bytes:
        return self._base.serialize(self._to_dict(track))

    @serialize.register       # будет срабатывать на любые list (в том числе list[Track])
    def _(self, tracks: list) -> bytes:
        return self._base.serialize([self._to_dict(t) for t in tracks])

    @singledispatchmethod
    def deserialize(self, data: bytes) -> Any:
        return self._base.deserialize(data)

    @deserialize.register     # single track
    def _(self, data: bytes) -> Optional[Track]:
        decoded = self._base.deserialize(data, dict)
        return None if decoded is None else self._from_dict(decoded)

    @deserialize.register     # list of tracks
    def _(self, data: bytes) -> list[Track]:
        decoded = self._base.deserialize(data, list)
        return [self._from_dict(d) for d in decoded]

    def _to_dict(self, track: Track) -> dict:
        return {
            "track_id": track.track_id,
            "title": track.title,
            "duration": track.duration.value,
            "artists": [vars(a) for a in track.artists],
            "genres":  [vars(g) for g in track.genres],
            "explicit": track.explicit,
            "release_date": track.release_date,
            "created_at": track.created_at,
        }

    def _from_dict(self, d: dict) -> Track:
        artists = [ArtistInfo(**a) for a in d["artists"]]
        genres  = [Genre(**g) for g in d["genres"]]
        return Track(
            track_id=d["track_id"],
            title=d["title"],
            duration=DurationMs(d["duration"]),
            artists=artists,
            genres=genres,
            explicit=bool(d["explicit"]),
            release_date=date.fromisoformat(d["release_date"]) if d["release_date"] else None,
            created_at=datetime.fromisoformat(d["created_at"]) if d["created_at"] else None,
        )
