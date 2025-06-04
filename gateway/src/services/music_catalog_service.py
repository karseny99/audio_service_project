from grpc import RpcError
from src.core.dependencies.grpc_clients import get_music_catalog_stub
from src.protos.user_context.generated import track_pb2

def get_tracks_by_artist(artist_id: int, offset: int, limit: int):
    stub = get_music_catalog_stub()
    request = track_pb2.GetTracksByArtistRequest(
        artist_id=artist_id,
        offset=offset,
        limit=limit
    )
    try:
        return stub.GetTracksByArtist(request)
    except RpcError as e:
        raise RuntimeError(f"Music Catalog Service error: {e.code().name}")

def get_tracks_by_genre(genre_id: int, offset: int, limit: int):
    stub = get_music_catalog_stub()
    request = track_pb2.GetTracksByGenreRequest(
        genre_id=genre_id,
        offset=offset,
        limit=limit
    )
    try:
        return stub.GetTracksByGenre(request)
    except RpcError as e:
        raise RuntimeError(f"Music Catalog Service error: {e.code().name}")


def get_track_by_id(track_id: int):
    stub = get_music_catalog_stub()
    request = track_pb2.GetTrackRequest(
        track_id=track_id,
    )
    response = stub.GetTrack(request)
    return response
