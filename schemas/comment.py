from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CommentCreate(BaseModel):
    content: str = Field(...)
    parent_id: Optional[int] = None


class CommentRead(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int
    parent_id: Optional[int]


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class CommentDelete(BaseModel):
    comment: CommentRead
    message: str
