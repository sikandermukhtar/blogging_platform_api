from config.base import Base
from sqlalchemy import text, DateTime, ForeignKey, Table, Column


blog_likes = Table(
    "blog_likes",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("blog_id", ForeignKey("blogs.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "created_at", DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    ),
)
