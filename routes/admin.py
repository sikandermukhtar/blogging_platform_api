from fastapi import APIRouter, Depends
from models import (
    User,
    Blog,
    Comment,
    BlogLike,
    CommentLike,
    FlaggedBlog,
    FlaggedComment,
    Role,
)
from sqlalchemy.orm import Session
from database import get_db
from schemas.admin import StatsResponse
from utils.user import allowed_role

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=StatsResponse)
def get_stats(
    db: Session = Depends(get_db), current_user: User = Depends(allowed_role("admin"))
):
    users = db.query(User).all()
    user_count = len(users)

    blogs = db.query(Blog).all()
    blog_count = len(blogs)

    blog_likes = db.query(BlogLike).all()
    blog_likes_count = len(blog_likes)

    comments = db.query(Comment).all()
    comments_count = len(comments)

    comment_likes = db.query(CommentLike).all()
    comment_likes_count = len(comment_likes)

    flagged_blogs = db.query(FlaggedBlog).all()
    flagged_blogs_count = len(flagged_blogs)

    flagged_comments = db.query(FlaggedComment).all()
    flagged_comments_count = len(flagged_comments)

    roles = db.query(Role).all()
    total_roles_count = len(roles)

    return StatsResponse(
        total_users=user_count,
        total_blog_posts=blog_count,
        total_blog_likes=blog_likes_count,
        total_comments=comments_count,
        total_comment_likes=comment_likes_count,
        flagged_blogs=flagged_blogs_count,
        flagged_comments=flagged_comments_count,
        total_roles=total_roles_count
    )
