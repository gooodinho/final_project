import sqlite3
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from filters import AdminFilter
from loader import dp, db, bot


@dp.message_handler(CommandStart(), AdminFilter())
async def bot_start_admin(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    if not db.select_user(user_id=user_id):
        try:
            db.add_user(user_id, username, full_name)
        except sqlite3.IntegrityError as err:
            print(err)
    count_users = db.count_users()[0]
    bot_username = (await bot.get_me()).username
    id_referral = db.get_id(user_id)[0]
    bot_link = "https://t.me/{bot_username}?start={id_referral}".format(
        bot_username=bot_username,
        id_referral=id_referral
    )
    balance = db.check_balance(user_id)[0]
    text = f"""
    Сейчас в базе {count_users} человек!

    Ваша реферальная ссылка: {bot_link}
    Проверить рефералов можно по команде: /referrals

    Ваш баланс: {balance} монет.
            """
    await message.answer(f"Добро пожаловать, <b>Администратор - {full_name}!</b>"
                         f"{text}")


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    # SET ARGS
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    # CHECK IF IN DB
    if not db.select_user(user_id=user_id):
        # CHECK REFERRAL
        try:
            referral = message.get_args()
        except ValueError:
            await message.answer(
                "Чтобы использовать этого бота введите код приглашения, либо пройдите по реферальной ссылке")
            return

        try:
            # ADD USER
            db.add_user(user_id, username, full_name, referral)
            await message.answer("Добавлен в базу!")
            # ADD ADMIN NOTIFY !!!!!!!!!
        except sqlite3.IntegrityError as err:
            print(err)
    count_users = db.count_users()[0]
    bot_username = (await bot.get_me()).username
    id_referral = db.get_id(user_id)[0]
    bot_link = "https://t.me/{bot_username}?start={id_referral}".format(
        bot_username=bot_username,
        id_referral=id_referral
    )
    balance = db.check_balance(user_id)[0]
    text = f"""
Сейчас в базе {count_users} человек!

Ваша реферальная ссылка: {bot_link}
Проверить рефералов можно по команде: /referrals

Ваш баланс: {balance} монет.
        """
    await message.answer(text)



# @dp.message_handler(CommandStart(deep_link="connect_user"))
# async def connect_user(message: types.Message):
#     allowed_users.append(message.from_user.id)
#     await message.answer("Vu podkluchenu",
#                          reply_markup=InlineKeyboardMarkup(
#                              inline_keyboard=[
#                                  [
#                                  InlineKeyboardButton(text="Voiti v inline rejim",
#                                                       switch_inline_query_current_chat="Zapros")
#                                  ]
#                              ]
#                          ))
