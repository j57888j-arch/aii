from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.users import get_user_by_telegram_id


class UserLoaderMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        session: AsyncSession | None = data.get("session")
        user = getattr(event, "from_user", None)
        data["db_user"] = (
            await get_user_by_telegram_id(session, user.id)
            if session is not None and user is not None
            else None
        )
        return await handler(event, data)
