from dataclasses import dataclass
from google.protobuf.message import Message

class UserEvent:
    """Базовый класс для событий"""
    pass

@dataclass
class UserRegistered(UserEvent):
    user_id: str
    email: str
    username: str
   
@dataclass 
class UserDeleted(UserEvent):
    user_id: str