from src.domain.events.handlers import EventHandler
from src.infrastructure.events.converters import UserEventConverter

class UserDeletedHandler(EventHandler):
    def __init__(self, use_case):
        self._use_case = use_case

    async def handle(self, proto_event) -> None:
        domain_event = UserEventConverter.convert_user_deleted(proto_event)
        await self._use_case.execute(domain_event)
