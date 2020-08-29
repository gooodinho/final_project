from asyncio import sleep

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from loader import dp, db, bot

from keyboards.default.cancel_promo import cancel_menu

from filters import AdminFilter

from states.add_item import AddItem


@dp.message_handler(text="Отмена", state=AddItem)
async def cancel_action(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(Command("add_item"), AdminFilter())
async def add_new_item(message: types.Message):
    await message.answer("Пришлите название товара:", reply_markup=cancel_menu)
    await AddItem.Name.set()


@dp.message_handler(AdminFilter(), state=AddItem.Name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name.capitalize())
    await message.answer(f"Название товара: {name}\nПришлите фотографию товара:")
    await AddItem.Photo.set()


@dp.message_handler(AdminFilter(), state=AddItem.Photo, content_types=types.ContentType.PHOTO)
async def get_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    name = data.get("name")
    await message.answer_photo(
        photo=photo,
        caption=f"Название: {name}\nПришлите описание товара"
    )
    await state.update_data(photo=photo)
    await AddItem.Description.set()


@dp.message_handler(AdminFilter(), state=AddItem.Description)
async def get_desc(message: types.Message, state: FSMContext):
    description = message.text
    await message.answer(f"Описание: {description}\nПришлите цену товара в копейках")
    await state.update_data(description=description)
    await AddItem.Price.set()


@dp.message_handler(AdminFilter(), state=AddItem.Price)
async def get_price(message: types.Message, state: FSMContext):
    # data = await state.get_data()
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return
    await state.update_data(price=price)

    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(
                text="Да",
                callback_data="confirm"
            )],
            [types.InlineKeyboardButton(
                text="Ввести заново",
                callback_data="change"
            )]
        ]
    )
    await message.answer(f"Цена: {price:,}\nПодтверждаете?", reply_markup=markup)
    await AddItem.Confirm.set()


@dp.callback_query_handler(AdminFilter(), text_contains="change", state=AddItem.Confirm)
async def change_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите заново цену товара в копейках")
    await AddItem.Price.set()


@dp.callback_query_handler(AdminFilter(), text_contains="confirm", state=AddItem.Confirm)
async def confirm(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    name = data.get("name")
    photo = data.get("photo")
    description = data.get("description")
    price = data.get("price")
    db.add_item(name, photo, price, description)
    await call.message.answer("Товар удачно создан", reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(Command("items"), AdminFilter())
async def show_all_items(message: types.Message):
    all_items = db.select_all_items()
    text = "<b>{name}</b>\n<i>{description}</i>\n<b>Цена:</b> \t{price:,}"
    for item in all_items:
        await message.answer_photo(
            photo=item[2],
            caption=text.format(name=item[1],
                                description=item[3],
                                price=item[4]/100)
        )
        await sleep(0.3)