from aiogram import Router
from aiogram.types import Message

from keyboards.main_menu import main_menu
from database import connect

router = Router()


@router.message(lambda m: m.text == "/start")
async def start(message: Message):

    db = await connect()

    await db.execute(
        """
        INSERT OR IGNORE INTO users
        (
            user_id,
            username
        )
        VALUES(?,?)
        """,
        (
            message.from_user.id,
            message.from_user.username
        )
    )

    await db.commit()
    await db.close()

    await message.answer(
        """
👋 Welcome to Alkot SMM Services

🚀 Fast Instagram Growth

Available Services:

👁 Reel Views
❤️ Likes
📤 Shares
👥 Followers

Use the menu below to continue.
""",
        reply_markup=main_menu
    )