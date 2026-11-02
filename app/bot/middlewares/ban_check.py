from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from app.core.i18n.loader import translate


class BanCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("db_user")
        if user is not None and user.is_banned:
            text = translate(user.language, "blocked")
            if isinstance(event, CallbackQuery):
                await event.answer(text, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(text)
            return None
        return await handler(event, data)
