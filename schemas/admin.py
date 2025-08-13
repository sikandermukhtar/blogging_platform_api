from pydantic import BaseModel


class StatsResponse(BaseModel):
    total_users: int
    total_blog_posts: int
    total_blog_likes: int
    total_comments: int
    total_comment_likes: int
    flagged_blogs: int
    flagged_comments: int
    total_roles: int