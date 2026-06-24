from aiogram import Router, Bot
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext

from states.recharge_state import RechargeState
from config import ADMIN_ID, UPI_ID

router = Router()


# =====================================
# DEPOSIT BUTTON
# =====================================

@router.message(lambda m: m.text == "💰 Deposit")
async def deposit(message: Message, state: FSMContext):

    await message.answer(
        f"""
💰 Deposit

Send payment to:

UPI ID:
{UPI_ID}

After payment send screenshot.
"""
    )

    await state.set_state(
        RechargeState.waiting_screenshot
    )


# =====================================
# RECEIVE SCREENSHOT
# =====================================

@router.message(
    RechargeState.waiting_screenshot
)
async def receive_screenshot(
    message: Message,
    state: FSMContext,
    bot: Bot
):

    if not message.photo:
        return await message.answer(
            "❌ Please send screenshot image"
        )

    user_id = message.from_user.id
    username = message.from_user.username

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Approve",
                    callback_data=f"approve_deposit_{user_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Reject",
                    callback_data=f"reject_deposit_{user_id}"
                )
            ]
        ]
    )

    await bot.send_photo(
        ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=
        f"""
💰 New Deposit Request

👤 User:
@{username}

🆔 User ID:
{user_id}
""",
        reply_markup=kb
    )

    await message.answer(
        """
✅ Screenshot Submitted

Please wait for admin approval.
"""
    )

    await state.clear()