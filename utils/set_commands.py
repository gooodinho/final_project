from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Перезапусить бота"),
        types.BotCommand("referrals", "Проверить рефералов"),
        types.BotCommand("promo", "Установить/показать промокод"),
        types.BotCommand("help", "Получить справку")
    ])
