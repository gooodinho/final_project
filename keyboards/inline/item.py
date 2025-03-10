from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

buying_item = CallbackData("buy", "id")
show_item = CallbackData("show", "id")


def buy_keyboard(item_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Купить",
                callback_data=buying_item.new(id=item_id)
            )]
        ]
    )
    return keyboard


def show_keyboard(item_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Показать товар",
                callback_data=show_item.new(id=item_id)
            )]
        ]
    )
    return keyboard
