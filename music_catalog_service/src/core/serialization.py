from abc import abstractmethod
from typing import Protocol, runtime_checkable
from google.protobuf.message import Message

@runtime_checkable
class Serializer(Protocol):
    @abstractmethod
    def serialize(self, event) -> bytes:
        pass


# class ProtobufSerializer:
#     def serialize(self, event) -> bytes:
#         if not hasattr(event, 'to_proto'):
#             raise ValueError("Event cannot be converted to protobuf")
        
#         proto_message = event.to_proto()
#         if not isinstance(proto_message, Message):
#             raise ValueError("to_proto() must return a protobuf message")
        
#         return proto_message.SerializeToString()