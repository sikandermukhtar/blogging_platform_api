from config.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, text, DateTime, ForeignKey
from datetime import datetime
from pydantic import EmailStr
from typing import TYPE_CHECKING, List
from .blog_like import blog_likes
from .comment_like import comment_likes

if TYPE_CHECKING:
    from .role import Role
    from .blog import Blog


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[EmailStr] = mapped_column(
        String, index=True, unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="RESTRICT"),
        server_default=text("5"),
        nullable=False,
    )

    role: Mapped["Role"] = relationship("Role", back_populates="users")
    blogs: Mapped[List["Blog"]] = relationship(
        "Blog", back_populates="owner", cascade="all, delete-orphan"
    )
    liked_blogs = relationship("Blog", secondary=blog_likes, back_populates="likes")
    flagged_blogs = relationship(
        "FlaggedBlog", back_populates="user", passive_deletes=True
    )
    comments = relationship(
        "Comment", back_populates="owner", cascade="all, delete-orphan"
    )
    liked_comments = relationship(
        "Comment", secondary=comment_likes, back_populates="likes"
    )
    flagged_comments = relationship(
        "FlaggedComment", back_populates="user", passive_deletes=True
    )
