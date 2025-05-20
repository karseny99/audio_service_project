from dataclasses import dataclass
from datetime import datetime

from src.domain.user_likes.value_objects import TrackId, UserId


@dataclass(frozen=True)
class UserLike:
    """Модель отдельного лайка пользователя"""
    user_id: UserId
    track_id: TrackId
    liked_at: datetime

    