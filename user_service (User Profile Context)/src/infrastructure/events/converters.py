from functools import singledispatchmethod

from src.core.config import settings
from src.infrastructure.events.base_converter import BaseEventConverter

from src.core.protos.generated.events_pb2 import (
    UserDeleted as UserDeletedProto,
    UserRegistered as UserRegisteredProto
)

from src.domain.events.events import UserDeleted, UserRegistered, UserEvent

class UserEventConverters(BaseEventConverter):
    @singledispatchmethod
    @staticmethod
    def to_proto(event):
        raise NotImplementedError(f"No proto converter for {type(event).__name__}")

    @to_proto.register
    @staticmethod
    def _(event: UserDeleted) -> UserDeletedProto:
        return UserDeletedProto(user_id=event.user_id)

    @to_proto.register
    @staticmethod
    def _(event: UserRegistered) -> UserRegisteredProto:
        return UserRegisteredProto(
            user_id=event.user_id,
            # email=event.email,
            # username=event.username
        )

    @staticmethod
    def get_headers(event: UserEvent) -> dict:
        return {settings.EVENT_HEADER: event.__class__.__name__}
