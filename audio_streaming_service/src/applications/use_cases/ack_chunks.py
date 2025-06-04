from src.core.logger import logger

from src.domain.events.publisher import EventPublisher
from src.domain.events.events import ChunksAckEvent
from src.domain.stream.models import StreamSession

class AcknowledgeChunksUseCase:
    def __init__(
        self,
        event_publisher: EventPublisher,
    ):
        self._event_publisher = event_publisher

    async def execute(self, received_count: int, session: StreamSession) -> None:
        logger.info(f"in session {session.session_id} acknowledged {received_count} chunks")
        await self._event_publisher.publish(
            event=ChunksAckEvent(
                session_id=session.session_id,
                acked_chunk_count=received_count, 
                timestamp=session.started_at,
            ),
            key=str(session.user_id)
        )
