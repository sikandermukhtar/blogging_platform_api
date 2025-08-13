from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FlaggedCommentRead(BaseModel):
    id: int
    created_at: datetime

    comment_id: int
    user_id: Optional[int] = None
