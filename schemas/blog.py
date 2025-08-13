from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class BlogCreate(BaseModel):
    title: str = Field(..., max_length=120)
    content: str = Field(...)
    main_image_url: Optional[str] = None


class BlogRead(BaseModel):
    id: int
    title: str
    content: str
    main_image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    main_image_url: Optional[str] = None


class BlogDelete(BaseModel):
    blog: BlogRead
    message: str
