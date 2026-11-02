from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.onboarding import goal_keyboard, language_keyboard
from app.bot.states import Onboarding
from app.core.i18n.loader import translate
from app.services.users import finish_onboarding, get_or_create_user, set_user_language

router = Router(name="start")
_ALLOWED_LANGUAGES = {"uz", "ru", "en"}
_ALLOWED_GOALS = {"study", "job", "code"}


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if message.from_user is None:
        return
    user = await get_or_create_user(
        session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        language_code=message.from_user.language_code,
    )
    if user.onboarding_completed:
        await message.answer(translate(user.language, "welcome_back"))
        return
    await state.set_state(Onboarding.language)
    await message.answer(translate("uz", "choose_language"), reply_markup=language_keyboard())


@router.callback_query(Onboarding.language, F.data.startswith("onb:lang:"))
async def choose_language_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    if callback.from_user is None:
        await callback.answer()
        return
    language = callback.data.rsplit(":", maxsplit=1)[-1] if callback.data else ""
    if language not in _ALLOWED_LANGUAGES:
        await callback.answer("Invalid language", show_alert=True)
        return
    await set_user_language(session, callback.from_user.id, language)
    await state.set_state(Onboarding.goal)
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            translate(language, "choose_goal"),
            reply_markup=goal_keyboard(language),
        )
    await callback.answer(translate(language, "language_saved"))


@router.callback_query(Onboarding.goal, F.data.startswith("onb:goal:"))
async def choose_goal_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    if callback.from_user is None:
        await callback.answer()
        return
    goal = callback.data.rsplit(":", maxsplit=1)[-1] if callback.data else ""
    if goal not in _ALLOWED_GOALS:
        await callback.answer("Invalid goal", show_alert=True)
        return
    await finish_onboarding(session, callback.from_user.id, goal)
    await state.clear()
    language = "uz"
    from app.services.users import get_user_by_telegram_id

    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if user:
        language = user.language
    if isinstance(callback.message, Message):
        await callback.message.edit_text(translate(language, "onboarding_done"))
        await callback.message.answer(translate(language, "home_phase1"))
    await callback.answer(translate(language, "goal_saved"))
