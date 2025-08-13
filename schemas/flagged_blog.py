from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FlaggedBlogRead(BaseModel):
    id: int
    created_at: datetime

    blog_id: int
    user_id: Optional[int] = None
