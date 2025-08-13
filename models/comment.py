from config.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, text, DateTime, ForeignKey
from datetime import datetime
from typing import TYPE_CHECKING
from .comment_like import comment_likes
from typing import List

if TYPE_CHECKING:
    from .user import User
    from .blog import Blog


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id", ondelete="CASCADE"))
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )

    owner: Mapped["User"] = relationship("User", back_populates="comments")
    blog: Mapped["Blog"] = relationship("Blog", back_populates="comments")
    # self-referential relationship
    parent: Mapped["Comment"] = relationship(
        "Comment", remote_side=[id], back_populates="replies"
    )
    replies: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    likes: Mapped[List["User"]] = relationship(
        "User", secondary=comment_likes, back_populates="liked_comments"
    )
    flagged_comments = relationship(
        "FlaggedComment", back_populates="comment", cascade="all, delete-orphan"
    )
