from dataclasses import dataclass
from google.protobuf.message import Message

class UserEvent:
    """Базовый класс для событий"""
    pass

@dataclass
class UserRegistered(UserEvent):
    user_id: str

@dataclass 
class UserDeleted(UserEvent):
    user_id: str