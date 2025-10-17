from aiogram.fsm.state import State, StatesGroup


class DraftState(StatesGroup):
    selecting_side = State()
    drafting = State()
