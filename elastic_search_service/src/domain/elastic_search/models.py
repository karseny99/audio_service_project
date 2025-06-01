from dataclasses import dataclass

@dataclass(frozen=True)
class TrackId:
    value: int

@dataclass(frozen=True)
class ArtistName:
    value: str

@dataclass(frozen=True)
class GenreName:
    value: str
