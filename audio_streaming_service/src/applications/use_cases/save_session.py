from src.core.logger import logger
from src.domain.stream.models import StreamSession
from src.domain.stream.repository import StreamingRepository

class SaveSessionUseCase:
    def __init__(
        self,
        session_repo: StreamingRepository,
    ):
        self._session_repo = session_repo 

    async def execute(self, session: StreamSession) -> None:
        await self._session_repo.save(session)
        logger.info(f"Session {session.session_id} saved")

