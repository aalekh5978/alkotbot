from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


@router.message(lambda m: m.text == "📸 Instagram Services")
async def instagram_services(message: Message):

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👁 Instagram Reel Views - ₹1/1K",
                    callback_data="service_10695"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❤️ Instagram Likes - ₹8/1K",
                    callback_data="service_13914"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📤 Instagram Shares - ₹3/1K",
                    callback_data="service_12287"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Instagram Followers - ₹50/1K",
                    callback_data="service_13541"
                )
            ]
        ]
    )

    await message.answer(
        "📸 Select Instagram Service",
        reply_markup=kb
    )