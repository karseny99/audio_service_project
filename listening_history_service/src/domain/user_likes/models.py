from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from src.domain.user_likes.value_objects import TrackId, UserId
from src.core.exceptions import TrackAlreadyLiked


@dataclass(frozen=True)
class UserLike:
    """Модель отдельного лайка пользователя"""
    user_id: UserId
    track_id: TrackId
    liked_at: datetime

    