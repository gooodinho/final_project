from loader import db


async def on_startup(dp):
    import filters
    import middlewares
    filters.setup(dp)
    middlewares.setup(dp)

    from utils.notify_admins import admin_notify
    try:
        db.create_table_users()
    except Exception as e:
        print(e)
    try:
        db.create_item_table()
    except Exception as e:
        print(e)

    print(db.select_all_items())
    print(db.select_all_users())
    await admin_notify(dp, "Бот запущен!")


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
