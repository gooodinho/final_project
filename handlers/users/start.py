from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from data.config import PROVIDER_TOKEN
from data.items_payment import get_prices, POST_REG_SHIPPING, POST_FAST_SHIPPING, PICKUP_SHIPPING
from loader import dp, db, bot

from filters import AdminFilter

from keyboards.default.cancel_promo import cancel_menu
from keyboards.inline.promo import send_promo, change_to_inline
from keyboards.inline.promo_callback import promo_callback
from keyboards.inline.item import buy_keyboard

from utils.notify_admins import ref_notify


# TEST INVOICES ------------------

@dp.message_handler(CommandStart(deep_link="show"), state="showing")
async def show_invoice(message: types.Message, state: FSMContext):
    if PROVIDER_TOKEN.split(':')[1] == 'TEST':
        await message.answer('test invoice')

    data = await state.get_data()
    item_id = data.get("id")
    item = db.select_item(id=item_id)
    await bot.send_invoice(
        message.chat.id,
        title=item[1],
        description=item[3],
        provider_token=PROVIDER_TOKEN,
        currency='uah',
        photo_url=item[5],
        photo_height=412,  # !=0/None, иначе изображение не покажется
        photo_width=412,
        photo_size=412,
        is_flexible=True,  # True если конечная цена зависит от способа доставки
        prices=get_prices(item[1], item[4]),
        start_parameter=f"str_prm_{item_id}",
        payload=f'invoice_{item_id}'
    )
    await state.finish()


@dp.shipping_query_handler()
async def choose_shipping(query: types.ShippingQuery):
    if query.shipping_address.country_code == "UA":
        await bot.answer_shipping_query(shipping_query_id=query.id,
                                        shipping_options=[
                                            POST_REG_SHIPPING,
                                            POST_FAST_SHIPPING,
                                            PICKUP_SHIPPING
                                        ],
                                        ok=True)
    else:
        await bot.answer_shipping_query(shipping_query_id=query.id,
                                        shipping_options=[
                                            POST_REG_SHIPPING,
                                            POST_FAST_SHIPPING
                                        ],
                                        ok=True)


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query_id=query.id,
                                        ok=True)
    await bot.send_message(chat_id=query.from_user.id, text="Спасибо за покупку!")

# /START FROM INLINE MODE WITH SELECTED ITEM DESCRIPTION
# @dp.message_handler(CommandStart(deep_link="show"), state="showing")
# async def show_item(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     item_id = data.get("id")
#     item = db.select_item(id=item_id)
#     text = "<b>{name}</b>\n\n<i>{description}</i>\n\n<b>Цена:</b> \t{price:,}"
#     await message.answer_photo(
#             photo=item[2],
#             caption=text.format(name=item[1],
#                                 description=item[3],
#                                 price=item[4]/100),
#             reply_markup=buy_keyboard(item_id)
#     )
#     await state.finish()


# /START FOR ADMIN
@dp.message_handler(CommandStart(), AdminFilter())
async def bot_start_admin(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    if not db.select_user(user_id=user_id):
        db.add_user(user_id, username, full_name)
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
    Посмотреть все товары по команде: /items
    Добавить товар по команде: /add_item

    Ваш баланс: {balance} монет.
            """
    await message.answer(f"Добро пожаловать, <b>Администратор - {full_name}!</b>"
                         f"{text}")


# DEFAULT /START
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
            # CHECK IF FROM INLINE MODE
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

        # ADD USER TO DB
        db.add_user(user_id, username, full_name, referral)
        await message.answer("Вы зарегистрированы!")
        # ADD MONEY FOR REFERRAL ADN NOTIFY USER
        ref_user_id = db.get_user_id(referral)[0]
        db.add_money(10, ref_user_id)
        await ref_notify(dp, ref_user_id, f"У вас новый реферал, +10 монет!")

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
    await message.answer(text, reply_markup=change_to_inline)


@dp.message_handler(text="Отмена", state="send_promo")
async def cancel_action(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=ReplyKeyboardRemove())


@dp.callback_query_handler(promo_callback.filter(command="send_promo"))
async def get_promo(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=5)
    await state.set_state("send_promo")
    await bot.send_message(chat_id=call.message.chat.id, text="Отправьте промокод:",
                           reply_markup=cancel_menu)


@dp.message_handler(state="send_promo")
async def add_user_promo(message: types.Message, state: FSMContext):
    # SET ARGS
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    # CHECK PROMO
    if not db.check_promo(message.text):
        await message.answer("Такого промокода не существует.", reply_markup=ReplyKeyboardRemove())
    else:
        # ADD USER TO DB BY PROMO
        referral = db.check_promo(message.text)[0]
        db.add_user(user_id, username, full_name, referral)
        await message.answer("Вы зарегистрированы!")
        # ADD MONEY FOR REFERRAL ADN NOTIFY USER
        ref_user_id = db.get_user_id(referral)[0]
        db.add_money(10, ref_user_id)
        await ref_notify(dp, ref_user_id, f"У вас новый реферал, +10 монет!")
    await state.finish()
