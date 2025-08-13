from config.base import Base
from sqlalchemy import text, DateTime, ForeignKey, Table, Column

comment_likes = Table(
    "comment_likes",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "comment_id", ForeignKey("comments.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "created_at", DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    ),
)
