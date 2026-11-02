from aiogram.utils.keyboard import InlineKeyboardBuilder


def language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O‘zbekcha", callback_data="onb:lang:uz")
    builder.button(text="🇷🇺 Русский", callback_data="onb:lang:ru")
    builder.button(text="🇬🇧 English", callback_data="onb:lang:en")
    builder.adjust(2, 1)
    return builder.as_markup()


def goal_keyboard(language: str):
    names = {
        "uz": (("📚 O‘qish", "study"), ("💼 Ish", "job"), ("💻 Dasturlash", "code")),
        "ru": (("📚 Учёба", "study"), ("💼 Работа", "job"), ("💻 Код", "code")),
        "en": (("📚 Study", "study"), ("💼 Job", "job"), ("💻 Coding", "code")),
    }
    builder = InlineKeyboardBuilder()
    for label, value in names.get(language, names["uz"]):
        builder.button(text=label, callback_data=f"onb:goal:{value}")
    builder.adjust(2, 1)
    return builder.as_markup()
