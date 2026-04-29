from aiogram.fsm.state import State, StatesGroup


class AddReminderStates(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_time = State()


class DeleteReminderStates(StatesGroup):
    waiting_id = State()
