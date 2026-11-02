from __future__ import annotations

import secrets
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


def _new_referral_code() -> str:
    return secrets.token_urlsafe(9).replace("-", "").replace("_", "")[:12]


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    return await session.scalar(select(User).where(User.telegram_id == telegram_id))


async def get_or_create_user(
    session: AsyncSession,
    *,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    language_code: str | None,
) -> User:
    language = (language_code or "uz").lower().split("-", maxsplit=1)[0]
    if language not in {"uz", "ru", "en"}:
        language = "uz"
    values = {
        "telegram_id": telegram_id,
        "username": username,
        "first_name": first_name,
        "language": language,
        "timezone": "Asia/Tashkent",
        "referral_code": _new_referral_code(),
        "last_seen_at": datetime.now(UTC),
    }
    statement = pg_insert(User).values(**values)
    statement = statement.on_conflict_do_update(
        index_elements=[User.telegram_id],
        set_={
            "username": statement.excluded.username,
            "first_name": statement.excluded.first_name,
            "last_seen_at": statement.excluded.last_seen_at,
        },
    ).returning(User)
    result = await session.execute(statement.execution_options(populate_existing=True))
    user = result.scalar_one()
    await session.commit()
    return user


async def set_user_language(session: AsyncSession, telegram_id: int, language: str) -> None:
    await session.execute(update(User).where(User.telegram_id == telegram_id).values(language=language))
    await session.commit()


async def finish_onboarding(session: AsyncSession, telegram_id: int, goal: str) -> None:
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(onboarding_goal=goal, onboarding_completed=True)
    )
    await session.commit()
