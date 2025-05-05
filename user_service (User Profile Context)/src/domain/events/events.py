from dataclasses import dataclass
from google.protobuf.message import Message

class UserEvent:
    """Базовый класс для событий"""
    def to_proto(self) -> Message:
        raise NotImplementedError

@dataclass
class UserRegistered(UserEvent):
    user_id: str
    email: str
    username: str

    def to_proto(self) -> Message:
        from src.core.protos.generated.events_pb2 import UserRegistered as UserRegisteredProto
        
        return UserRegisteredProto(
            user_id=self.user_id,
        )
    
@dataclass 
class UserDeleted(UserEvent):
    user_id: str

    def to_proto(self) -> Message:
        from src.core.protos.generated.events_pb2 import UserDeleted as UserDeletedProto
        
        return UserDeletedProto(
            user_id=self.user_id,
        )
