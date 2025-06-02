from pydantic import BaseModel

class AddPlaylistRequest(BaseModel):
    playlist_id: int

class AddPlaylistResponse(BaseModel):
    message: str