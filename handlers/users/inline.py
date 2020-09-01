from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from keyboards.inline.item import show_keyboard, show_item
from loader import dp, db


@dp.inline_handler(text="")
async def empty_query(query: types.InlineQuery):
    user = query.from_user.id
    check_user = db.select_user(user_id=user)
    if check_user is None:
        await query.answer(
            results=[],
            switch_pm_text="Бот недоступен. Подключить",
            switch_pm_parameter="connect_user",
            cache_time=5
        )
        return
    items = db.select_all_items_abc()
    res = []
    for item in items:
        id = item[0]
        name = item[1]
        # photo_id = item[2]
        # description = item[3]
        price = item[4]/100
        url = item[5]
        inline_text = f"Цена:\t{price}"
        text = f"<b>{name}</b>\n\n<b>Цена:</b> \t{price:,}"
        # res.append(types.InlineQueryResultCachedPhoto(id=id, photo_file_id=photo_id, caption=text,
        #                                               parse_mode="HTML", reply_markup=show_keyboard(id)))
        res.append(types.InlineQueryResultArticle(id=id, title=name,
                                                  input_message_content=types.InputTextMessageContent(
                                                      message_text=text
                                                  ),
                                                  reply_markup=show_keyboard(id),
                                                  description=inline_text,
                                                  thumb_url=url))
    await query.answer(
        results=res,
        cache_time=5
    )


@dp.inline_handler()
async def some_query(query: types.InlineQuery):
    user = query.from_user.id
    check_user = db.select_user(user_id=user)
    if check_user is None:
        await query.answer(
            results=[],
            switch_pm_text="Бот недоступен. Подключить",
            switch_pm_parameter="connect_user",
            cache_time=5
        )
        return

    text = query.query
    if len(text) >= 2:
        items = db.search_items(text)
        res = []
        for item in items:
            id = item[0]
            name = item[1]
            # photo_id = item[2]
            url = item[5]
            description = item[3]
            price = item[4]/100
            inline_text = f"Цена:\t{price}"
            text = f"<b>{name}</b>\n\n<i>{description}</i>\n\n<b>Цена:</b> \t{price:,}"
            # markup = types.InlineKeyboardMarkup(
            #     inline_keyboard=[
            #         [types.InlineKeyboardButton(
            #             text="Показать товар",
            #             callback_data=show_item.new(id=id)
            #         )]
            #     ]
            # )
            res.append(types.InlineQueryResultArticle(id=id, title=name,
                                                      input_message_content=types.InputTextMessageContent(
                                                          message_text=text
                                                      ),
                                                      reply_markup=show_keyboard(id),
                                                      description=inline_text,
                                                      thumb_url=url))
        await query.answer(
            results=res,
            cache_time=5
        )


@dp.callback_query_handler(show_item.filter())
async def show_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    item_id = int(callback_data.get("id"))
    await state.set_state("showing")
    await state.update_data(id=item_id)
    await call.answer(url="https://t.me/final_shop_bot?start=show")

