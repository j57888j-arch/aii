from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    language = State()
    goal = State()
