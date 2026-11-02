from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n.loader import translate
from app.services.users import get_user_by_telegram_id

router = Router(name="menu")


@router.message(Command("menu"))
async def menu_handler(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    user = await get_user_by_telegram_id(session, message.from_user.id)
    language = user.language if user else "uz"
    await message.answer(translate(language, "menu_text"))
