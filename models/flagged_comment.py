from config.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, text, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime


class FlaggedComment(Base):
    __tablename__ = "flagged_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    comment = relationship("Comment", back_populates="flagged_comments")
    user = relationship("User", back_populates="flagged_comments")

    __table_args__ = (
        UniqueConstraint("user_id", "comment_id", name="uq_user_comment_flag"),
    )
