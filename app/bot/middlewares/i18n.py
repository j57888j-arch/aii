from aiogram import BaseMiddleware


class I18nMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("db_user")
        telegram_user = getattr(event, "from_user", None)
        language = getattr(user, "language", None) or getattr(telegram_user, "language_code", None) or "uz"
        language = language.lower().split("-", maxsplit=1)[0]
        data["language"] = language if language in {"uz", "ru", "en"} else "uz"
        return await handler(event, data)
