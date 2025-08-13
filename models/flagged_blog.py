from config.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, text, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime


class FlaggedBlog(Base):
    __tablename__ = "flagged_blogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    blog = relationship("Blog", back_populates="flagged_blogs")
    user = relationship("User", back_populates="flagged_blogs")

    __table_args__ = (UniqueConstraint("user_id", "blog_id", name="uq_user_blog_flag"),)
