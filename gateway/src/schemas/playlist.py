from pydantic import BaseModel

class AddPlaylistRequest(BaseModel):
    playlist_id: int

class AddPlaylistResponse(BaseModel):
    message: str

class CreatePlaylistReqest(BaseModel):
    user_id: str
    title: str
    is_public : bool


class CreatePlaylistResponse(BaseModel):
    status: str
    playlist_id: str
