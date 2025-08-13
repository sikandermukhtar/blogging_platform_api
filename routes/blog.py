from fastapi import APIRouter, HTTPException, Depends, status
from database import get_db
from sqlalchemy.orm import Session
from schemas.blog import BlogCreate, BlogRead, BlogUpdate, BlogDelete
from schemas.comment import CommentCreate, CommentRead, CommentUpdate, CommentDelete
from schemas.like import BlogLikeResponse, CommentLikeResponse
from models import Blog, User, Comment, FlaggedBlog, FlaggedComment
from utils.user import (
    get_current_user,
    allow_blog_owner_or_roles,
    allowed_role,
    allow_comment_owner_or_roles,
)
from typing import List
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

router = APIRouter(prefix="/blogs", tags=["Blogs"])


# -----------------------------------Blog------------------------------------------#
@router.get("/", response_model=List[BlogRead])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).all()
    if not blogs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No blog exists yet."
        )
    return blogs


@router.get("/{blog_id}", response_model=BlogRead)
def get_blog_with_id(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog doesn't exist"
        )
    return blog


@router.post("/", response_model=BlogRead)
def create_blog(
    blog: BlogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(allowed_role("author")),
):
    new_blog = Blog(
        title=blog.title,
        content=blog.content,
        main_image_url=blog.main_image_url,
        owner_id=current_user.id,
    )
    try:
        db.add(new_blog)
        db.commit()
        return new_blog
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error occured while adding new blog",
        )


def get_blog_by_id(blog_id: int, db: Session):
    return db.query(Blog).filter(Blog.id == blog_id).first()


@router.delete("/{blog_id}", response_model=BlogDelete)
def delete_blog(
    blog_id: int,
    blog=Depends(
        allow_blog_owner_or_roles(
            get_blog_by_id,
            owner_attribute="owner_id",
            allowed_roles=["admin", "moderator"],
        )
    ),
    db: Session = Depends(get_db),
):
    try:
        db.delete(blog)
        db.commit()
        return {"blog": blog, "messgae": "Blog successfully deleted"}
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete blog, error occured.",
        )


@router.patch("/{blog_id}", response_model=BlogRead)
def update_blog(
    blog_id: int,
    blog: BlogUpdate,
    existing_blog=Depends(
        allow_blog_owner_or_roles(
            get_blog_by_id, owner_attribute="owner_id", allowed_roles=[]
        )
    ),
    db: Session = Depends(get_db),
):
    new_data = blog.model_dump(exclude_unset=True)
    for key, value in new_data.items():
        setattr(existing_blog, key, value)
    existing_blog.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
        db.refresh(existing_blog)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update blog, an integrity error occurred",
        )

    return existing_blog


# --------------------------------Likes on posts -------------------------------------------------------


@router.post("/{blog_id}/like")
def like_post(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found"
        )

    if current_user in blog.likes:
        blog.likes.remove(current_user)
        action = "unliked"
    else:
        blog.likes.append(current_user)
        action = "liked"

    db.commit()
    db.refresh(blog)

    return {"message": f"Post {action} successfully."}


@router.get("/{blog_id}/likes", response_model=BlogLikeResponse)
def total_likes_on_post(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog doesn't exist"
        )

    return {
        "blog_id": blog.id,
        "likes_count": len(blog.likes),
        "user_ids": [user.id for user in blog.likes],
    }


# --------------------------Comments -------------------------------------------------------------------


@router.get("/{blog_id}/comments", response_model=List[CommentRead])
def get_all_comments_on_post(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post doesn't exist"
        )
    comments = blog.comments

    if not comments:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="No comments exist")
    return comments


@router.post("/{blog_id}/comments", response_model=CommentRead)
def create_comments_on_post(
    blog_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(allowed_role("admin", "moderator", "author", "user")),
):
    post = db.query(Blog).filter(Blog.id == blog_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post doesn't exist"
        )

    parent_id = comment.parent_id if comment.parent_id else None
    new_comment = Comment(
        content=comment.content,
        parent_id=parent_id,
        owner_id=current_user.id,
        blog_id=blog_id,
    )

    try:
        db.add(new_comment)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity issue occured.",
        )
    return new_comment


comment_router = APIRouter(prefix="/comments", tags=["Comments"])


def get_comment_by_id(comment_id: int, db: Session):
    return db.query(Comment).filter(Comment.id == comment_id).first()


@comment_router.delete("/{comment_id}", response_model=CommentDelete)
def comment_delete(
    comment_id: int,
    db: Session = Depends(get_db),
    comment=Depends(
        allow_comment_owner_or_roles(
            get_comment_by_id,
            owner_attribute="owner_id",
            allowed_roles=["admin", "moderator"],
        )
    ),
):
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    try:
        db.delete(comment)
        db.commit()
        return {"comment": comment, "message": "comment successfully deleted"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Integrity error occured."
        )


@comment_router.patch("/{comment_id}", response_model=CommentRead)
def comment_update(
    comment_id: int,
    new_comment: CommentUpdate,
    db: Session = Depends(get_db),
    comment=Depends(
        allow_comment_owner_or_roles(
            get_comment_by_id, owner_attribute="owner_id", allowed_roles=[]
        )
    ),
):
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    updated_data = new_comment.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(comment, key, value)

    comment.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(comment)
        return comment
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Integrity error occured."
        )


# --------------------------------------------- Likes on comments -------------------------------------------


@comment_router.post("/{comment_id}/like")
def like_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found"
        )

    if current_user in comment.likes:
        comment.likes.remove(current_user)
        action = "unliked"
    else:
        comment.likes.append(current_user)
        action = "liked"

    db.commit()
    db.refresh(comment)

    return {"message": f"Post {action} successfully."}


@comment_router.get("/{comment_id}/likes", response_model=CommentLikeResponse)
def total_likes_on_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog doesn't exist"
        )

    return {
        "comment_id": comment.id,
        "likes_count": len(comment.likes),
        "user_ids": [user.id for user in comment.likes],
    }


# ------------------------------------Flag comment and blog -----------------------------------------------------------


@router.post("/{blog_id}/flag")
def flag_blog(
    blog_id: int,
    current_user: User = Depends(allowed_role("moderator", "author", "user")),
    db: Session = Depends(get_db),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog doesn't exist"
        )

    if blog.owner_id == current_user.id:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot flag your own blog post.",
        )

    flagged_blog = FlaggedBlog(blog_id=blog.id, user_id=current_user.id)

    try:
        db.add(flagged_blog)
        db.commit()
        return {"message": "Blog post successfully flagged"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Integrity error occured"
        )


@comment_router.post("/{comment_id}/flag")
def flag_commemt(
    comment_id: int,
    current_user: User = Depends(allowed_role("moderator", "author", "user")),
    db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment doesn't exist"
        )

    if comment.owner_id == current_user.id:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot flag your own comment.",
        )

    flagged_comment = FlaggedComment(comment_id=comment.id, user_id=current_user.id)

    try:
        db.add(flagged_comment)
        db.commit()
        return {"message": "Comment successfully flagged"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Integrity error occured"
        )
