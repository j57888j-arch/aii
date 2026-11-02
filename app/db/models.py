from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_referred_by_id", "referred_by_id"),
        Index("ix_users_created_at", "created_at"),
        Index("ix_users_last_seen_at", "last_seen_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    username: Mapped[str | None] = mapped_column(String(64))
    first_name: Mapped[str | None] = mapped_column(String(128))
    language: Mapped[str] = mapped_column(String(2), nullable=False, default="uz", server_default=text("'uz'"))
    default_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="chat", server_default=text("'chat'"))
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Tashkent", server_default=text("'Asia/Tashkent'"))
    referral_code: Mapped[str] = mapped_column(String(24), nullable=False, unique=True)
    referred_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    is_banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    incognito: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    onboarding_goal: Mapped[str | None] = mapped_column(String(24))
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
