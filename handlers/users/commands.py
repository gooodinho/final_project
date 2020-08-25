from aiogram import types
from filters import AdminFilter
from aiogram.dispatcher.filters import Command
from loader import dp, db, bot


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

