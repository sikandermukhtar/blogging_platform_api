from pydantic import BaseModel
from typing import List


class BlogLikeResponse(BaseModel):
    blog_id: int
    likes_count: int
    user_ids: List[int]


class CommentLikeResponse(BaseModel):
    comment_id: int
    likes_count: int
    user_ids: List[int]
