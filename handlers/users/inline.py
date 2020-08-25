from aiogram import types

from data.config import allowed_users
from loader import dp


@dp.inline_handler(text="")
async def empty_query(query: types.InlineQuery):
    await query.answer(
        results=[
            types.InlineQueryResultArticle(
                id="unknown",
                title="Введите навзание товара",
                input_message_content=types.InputTextMessageContent(
                    message_text="lololo",
                )
            )
        ],
        cache_time=5
    )


@dp.inline_handler()
async def some_query(query: types.InlineQuery):
    user = query.from_user.id
    if user not in allowed_users:
        await query.answer(
            results=[],
            switch_pm_text="Bot nedostupen",
            switch_pm_parameter="connect_user",
            cache_time=5
        )
        return

    await query.answer(
        results=[
            types.InlineQueryResultArticle(
                id="1",
                title="Inline name",
                input_message_content=types.InputTextMessageContent(
                    message_text="message text"
                ),
                url="https://www.hltv.org/matches/2343390/nip-vs-natus-vincere-esl-one-cologne-2020-europe",
                thumb_url="https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.hltv.org%2Fteam%2F2647%2Fhltvorg&psig=AOvVaw1pdhtDv_pDQSemhxwKtqS1&ust=1598433813218000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCJiCkI6EtusCFQAAAAAdAAAAABAD",
                description="Desc in inline mode"
            ),
            types.InlineQueryResultVideo(
                id="4",
                video_url="https://pixabay.com/en/videos/download/video-10737_medium.mp4",
                caption="Video caption",
                title="video title",
                description="video description",
                thumb_url="https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.hltv.org%2Fteam%2F2647%2Fhltvorg&psig=AOvVaw1pdhtDv_pDQSemhxwKtqS1&ust=1598433813218000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCJiCkI6EtusCFQAAAAAdAAAAABAD",
                mime_type="video/mp4"
            )
        ]
    )


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