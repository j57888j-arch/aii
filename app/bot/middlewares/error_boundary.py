from __future__ import annotations

import logging

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, Update

from app.core.i18n.loader import translate

logger = logging.getLogger(__name__)


class ErrorBoundaryMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            return await handler(event, data)
        except Exception:
            update_id = event.update_id if isinstance(event, Update) else None
            logger.exception("Unhandled Telegram update error", extra={"update_id": update_id})
            language = data.get("language", "uz")
            notice = translate(language, "generic_error")
            try:
                if isinstance(event, Message):
                    await event.answer(notice)
                elif isinstance(event, CallbackQuery):
                    await event.answer(notice, show_alert=True)
                elif isinstance(event, Update):
                    if event.message:
                        await event.message.answer(notice)
                    elif event.callback_query:
                        await event.callback_query.answer(notice, show_alert=True)
            except Exception:
                logger.warning("Could not send fallback error message")
            return None
