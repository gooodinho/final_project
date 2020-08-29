import sqlite3

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from handlers.users.inline import buy_item
from loader import dp, db, bot

from filters import AdminFilter

from keyboards.default.cancel_promo import cancel_menu
from keyboards.inline.promo import send_promo
from keyboards.inline.promo_callback import promo_callback

from utils.notify_admins import ref_notify

buying_item = CallbackData("buy", "id")


@dp.message_handler(CommandStart(deep_link="show"), state="showing")
async def show_item(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item_id = data.get("id")
    item = db.select_item(id=item_id)
    text = "<b>{name}</b>\n<i>{description}</i>\n<b>Цена:</b> \t{price:,}"
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(
                text="Купить",
                callback_data=buying_item.new(id=id)
            )]
        ]
    )
    await message.answer_photo(
            photo=item[2],
            caption=text.format(name=item[1],
                                description=item[3],
                                price=item[4]/100),
            reply_markup=markup
    )
    await state.finish()


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
    promo = db.get_promo(user_id)[0]
    text = f"""
    Сейчас в базе {count_users} человек!

    Ваша реферальная ссылка: {bot_link}

    Ваш промокод: {promo}

    Проверить рефералов можно по команде: /referrals
    Установить/показать промокод по команде: /promo
    Добавить товар по команде: /add_item

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
            if referral == "connect_user":
                await message.answer(
                    "Чтобы использовать этого бота введите код приглашения, либо пройдите по реферальной ссылке",
                    reply_markup=send_promo)
                return
        except ValueError:
            await message.answer(
                "Чтобы использовать этого бота введите код приглашения, либо пройдите по реферальной ссылке",
                reply_markup=send_promo)
            return

        try:
            # ADD USER
            db.add_user(user_id, username, full_name, referral)
            await message.answer("Добавлен в базу!")
            ref_user_id = db.get_user_id(referral)[0]
            db.add_money(10, ref_user_id)
            await ref_notify(dp, ref_user_id, f"У вас новый реферал, +10 монет!")
        except sqlite3.IntegrityError as err:
            print(err)
    bot_username = (await bot.get_me()).username
    id_referral = db.get_id(user_id)[0]
    bot_link = "https://t.me/{bot_username}?start={id_referral}".format(
        bot_username=bot_username,
        id_referral=id_referral
    )
    balance = db.check_balance(user_id)[0]
    text = f"""
Ваша реферальная ссылка: {bot_link}
Проверить рефералов можно по команде: /referrals
Установить/показать промокод по команде: /promo

Ваш баланс: {balance} монет.
        """
    await message.answer(text)


@dp.message_handler(text="Отмена", state="send_promo")
async def cancel_action(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=ReplyKeyboardRemove())


@dp.callback_query_handler(promo_callback.filter(command="send_promo"))
async def get_promo(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    await state.set_state("send_promo")
    await bot.send_message(chat_id=call.message.chat.id, text="Отправьте промокод:",
                           reply_markup=cancel_menu)


@dp.message_handler(state="send_promo")
async def add_user_promo(message: types.Message, state: FSMContext):
    # SET ARGS
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    # ADD USER
    if not db.check_promo(message.text):
        await message.answer("Такого промокода не существует.", reply_markup=ReplyKeyboardRemove())
    else:
        referral = db.check_promo(message.text)[0]
        db.add_user(user_id, username, full_name, referral)
        await message.answer("Добавлен в базу!")
        ref_user_id = db.get_user_id(referral)[0]
        db.add_money(10, ref_user_id)
    await state.finish()

