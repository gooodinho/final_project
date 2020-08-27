from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.promo_callback import promo_callback

change_promo = InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text="Изменить промокод",
                                             callback_data=promo_callback.new(command="change_promo"))
                                     ]
                                 ])

send_promo = InlineKeyboardMarkup(inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text="Ввести промокод",
                                             callback_data=promo_callback.new(command="send_promo"))
                                     ]
                                 ])