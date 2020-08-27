from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

cancel_menu = ReplyKeyboardMarkup(resize_keyboard=True,
                                  keyboard=[
                                     [
                                         KeyboardButton(
                                             text="Отмена"
                                         )
                                     ]
                                 ])