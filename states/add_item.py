from aiogram.dispatcher.filters.state import StatesGroup, State


class AddItem(StatesGroup):
    Name = State()
    Photo = State()
    Description = State()
    Price = State()
    Confirm = State()