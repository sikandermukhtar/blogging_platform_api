from fastapi import APIRouter, HTTPException, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.flagged_blog import FlaggedBlogRead
from schemas.flagged_comment import FlaggedCommentRead
from typing import List
from models import Blog, User, Comment, FlaggedBlog, FlaggedComment
from utils.user import allowed_role
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/moderation", tags=["Moderation"])


@router.get("/blogs", response_model=List[FlaggedBlogRead])
def get_flagged_blog(
    db: Session = Depends(get_db),
    current_user: User = Depends(allowed_role("admin", "moderator")),
):
    flagged_blogs = db.query(FlaggedBlog).all()
    if not flagged_blogs:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED, detail="No blog is flagged yet."
        )

    return flagged_blogs


@router.get("/comments", response_model=List[FlaggedCommentRead])
def get_flagged_comment(
    db: Session = Depends(get_db),
    current_user: User = Depends(allowed_role("admin", "moderator")),
):
    flagged_comments = db.query(FlaggedComment).all()
    if not flagged_comments:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED, detail="No comment is flagged yet."
        )

    return flagged_comments


@router.post("/blogs/{blog_id}/review")
def approve_or_delete_flagged_blog(
    approved: bool,
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(allowed_role("admin", "moderator")),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    flagged = db.query(FlaggedBlog).filter(FlaggedBlog.blog_id == blog.id).first()

    if not flagged:
        raise HTTPException(status_code=404, detail="Blog is not flagged")

    if approved:
        try:
            db.delete(flagged)
            db.commit()
            return {"message": "Blog approved and removed from flagged list."}
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Integrity issue on flagged blogs, cannot perform action",
            )
    else:
        try:
            db.delete(blog)
            db.commit()
            return {"message": "Blog deleted due to disapproval"}
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Integrity issue on deleting blog, cannot perform action",
            )


@router.post("/comments/{comment_id}/review")
def approve_or_delete_flagged_comment(
    approved: bool,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(allowed_role("admin", "moderator")),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    flagged = (
        db.query(FlaggedComment).filter(FlaggedComment.comment_id == comment.id).first()
    )

    if not flagged:
        raise HTTPException(status_code=404, detail="Comment is not flagged")

    if approved:
        try:
            db.delete(flagged)
            db.commit()
            return {"message": "Comment approved and removed from flagged list."}
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Integrity issue on flagged comments, cannot perform action",
            )
    else:
        try:
            db.delete(comment)
            db.commit()
            return {"message": "Comment deleted due to disapproval"}
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Integrity issue on deleting comment, cannot perform action",
            )
