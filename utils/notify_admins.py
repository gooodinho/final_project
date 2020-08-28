import logging

from aiogram import Dispatcher

from data.config import admins


async def admin_notify(dp: Dispatcher, text):
    for admin in admins:
        try:
            await dp.bot.send_message(admin, text)

        except Exception as err:
            logging.exception(err)


async def ref_notify(dp: Dispatcher, user_id, text):
    try:
        await dp.bot.send_message(user_id, text)
    except Exception as err:
        logging.exception(err)