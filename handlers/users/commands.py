from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext

from keyboards.inline.promo_callback import promo_callback
from keyboards.inline.promo import change_promo
from loader import dp, db, bot
from keyboards.default.cancel_promo import cancel_menu
from aiogram.types import ReplyKeyboardRemove, CallbackQuery


@dp.message_handler(text="Отмена", state="set_promo")
async def cancel_action(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(Command("referrals"))
async def show_referrals(message: types.Message):
    user_id = message.from_user.id
    refs = db.check_referrals(user_id)
    print(refs)
    text = "Ваши рефералы:\n--------------\n"
    for num, ref in enumerate(refs):
        user = db.select_user(user_id=ref[0])
        text += str(num+1) + f". Username: @{user[2]}\nFull name: {user[3]}\n--------------\n"
    await message.answer(text)


@dp.message_handler(Command("promo"))
async def get_promo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    promo = db.get_promo(user_id=user_id)[0]
    if promo is not None:
        await message.answer(f"Ваш промокод: {promo}", reply_markup=change_promo)
    else:
        await message.answer("Придумайте промокод и отправьте", reply_markup=cancel_menu)
        await state.set_state("set_promo")


@dp.message_handler(state="set_promo")
async def set_promo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    promo = message.text
    db.set_promo(promo, user_id)
    await state.finish()
    await message.answer(f"Ваш промокод: {promo}", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(text="Отмена", state="set_promo")
async def cancel_action(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=ReplyKeyboardRemove())


@dp.callback_query_handler(promo_callback.filter(command="change_promo"))
async def chg_promo(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    await state.set_state("set_promo")
    await bot.send_message(chat_id=call.message.chat.id, text="Придумайте промокод и отправьте",
                           reply_markup=cancel_menu)
