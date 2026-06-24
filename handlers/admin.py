from aiogram import Router, Bot
from aiogram.types import (
    CallbackQuery,
    Message
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import connect
from config import ADMIN_ID

router = Router()


# ==========================================
# ADMIN STATE
# ==========================================

class AdminDepositState(StatesGroup):
    waiting_amount = State()


# ==========================================
# APPROVE DEPOSIT
# approve_deposit_USERID
# ==========================================

@router.callback_query(
    lambda c: c.data.startswith("approve_deposit_")
)
async def approve_deposit(
    callback: CallbackQuery,
    state: FSMContext
):

    if callback.from_user.id != ADMIN_ID:
        return

    user_id = int(
        callback.data.split("_")[2]
    )

    await state.update_data(
        target_user=user_id
    )

    await callback.message.answer(
        "💰 Enter amount to add:"
    )

    await state.set_state(
        AdminDepositState.waiting_amount
    )

    await callback.answer()


# ==========================================
# ENTER AMOUNT
# ==========================================

@router.message(
    AdminDepositState.waiting_amount
)
async def enter_amount(
    message: Message,
    state: FSMContext,
    bot: Bot
):

    if message.from_user.id != ADMIN_ID:
        return

    if not message.text.isdigit():
        return await message.answer(
            "❌ Enter numbers only"
        )

    amount = float(message.text)

    data = await state.get_data()

    user_id = data["target_user"]

    db = await connect()

    await db.execute(
        """
        UPDATE users
        SET balance = balance + ?
        WHERE user_id = ?
        """,
        (
            amount,
            user_id
        )
    )

    await db.commit()

    cur = await db.execute(
        """
        SELECT balance
        FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    balance = (
        await cur.fetchone()
    )[0]

    await db.close()

    await bot.send_message(
        user_id,
        f"""
✅ Deposit Approved

💰 Amount Added: ₹{amount}

💳 Current Balance:
₹{balance}
"""
    )

    await message.answer(
        f"✅ ₹{amount} added successfully"
    )

    await state.clear()


# ==========================================
# REJECT DEPOSIT
# reject_deposit_USERID
# ==========================================

@router.callback_query(
    lambda c: c.data.startswith(
        "reject_deposit_"
    )
)
async def reject_deposit(
    callback: CallbackQuery,
    bot: Bot
):

    if callback.from_user.id != ADMIN_ID:
        return

    user_id = int(
        callback.data.split("_")[2]
    )

    await bot.send_message(
        user_id,
        """
❌ Deposit Rejected

If you believe this is a mistake,
please contact support.
"""
    )

    await callback.message.edit_text(
        "❌ Deposit Rejected"
    )

    await callback.answer()


# ==========================================
# ADMIN PANEL
# ==========================================

@router.message(
    lambda m:
    m.text == "/admin"
)
async def admin_panel(
    message: Message
):

    if message.from_user.id != ADMIN_ID:
        return

    db = await connect()

    cur = await db.execute(
        "SELECT COUNT(*) FROM users"
    )

    users = (
        await cur.fetchone()
    )[0]

    cur = await db.execute(
        "SELECT COUNT(*) FROM orders"
    )

    orders = (
        await cur.fetchone()
    )[0]

    await db.close()

    await message.answer(
        f"""
🛠 Admin Panel

👥 Users: {users}
📦 Orders: {orders}

Admin ID:
{ADMIN_ID}
"""
    )