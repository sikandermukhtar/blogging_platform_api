from config.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, text, DateTime, ForeignKey, Text
from datetime import datetime
from .blog_like import blog_likes
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    main_image_url: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    owner: Mapped["User"] = relationship("User", back_populates="blogs")
    likes = relationship("User", secondary=blog_likes, back_populates="liked_blogs")
    flagged_blogs = relationship(
        "FlaggedBlog", back_populates="blog", cascade="all, delete-orphan"
    )
    comments = relationship(
        "Comment", back_populates="blog", cascade="all, delete-orphan"
    )
