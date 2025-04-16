# Helper for protobuf ↔ Python-Domainfrom datetime import datetime
from core.protobuf.generated import user_events_pb2

def serialize_user_registered(user_id: str, email: str) -> bytes:
    proto_msg = user_events_pb2.UserRegistered(
        user_id=user_id,
        email=email,
        timestamp=int(datetime.now().timestamp())
    )
    return proto_msg.SerializeToString()

def deserialize_user_registered(data: bytes) -> dict:
    proto_msg = user_events_pb2.UserRegistered()
    proto_msg.ParseFromString(data)
    return {
        "user_id": proto_msg.user_id,
        "email": proto_msg.email,
        "timestamp": proto_msg.timestamp
    }
