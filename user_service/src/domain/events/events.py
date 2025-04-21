# src/domain/events/events.py
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4
from src.core.protobuf.generated.user_events_pb2 import UserRegistered as UserRegisteredProto

@dataclass
class UserRegistered:
    user_id: int
    email: str
    username: str
    occurred_on: datetime = None
    event_id: str = None
    
    def __post_init__(self):
        self.event_id = self.event_id or str(uuid4())
        self.occurred_on = self.occurred_on or datetime.utcnow()
    
    def to_protobuf(self) -> UserRegisteredProto:
        proto = UserRegisteredProto()
        proto.event_id = self.event_id
        proto.user_id = str(self.user_id)
        proto.email = self.email
        proto.username = self.username
        proto.occurred_on.FromDatetime(self.occurred_on)
        return proto
    
    @classmethod
    def from_protobuf(cls, proto: UserRegisteredProto):
        return cls(
            event_id=proto.event_id,
            user_id=proto.user_id,
            email=proto.email,
            username=proto.username,
            occurred_on=proto.occurred_on.ToDatetime()
        )