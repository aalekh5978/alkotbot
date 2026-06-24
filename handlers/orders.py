from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states.order_state import OrderState
from database import connect
from config import API_URL, API_KEY

import requests

router = Router()


# ==========================================
# CANCEL CURRENT PROCESS
# ==========================================

@router.message(lambda m: m.text == "/cancel")
async def cancel(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "✅ Current process cancelled."
    )


# ==========================================
# SERVICE SELECTION
# ==========================================

@router.callback_query(lambda c: c.data.startswith("service_"))
async def select_service(
    callback: CallbackQuery,
    state: FSMContext
):

    service_id = int(
        callback.data.split("_")[1]
    )

    await state.update_data(
        service_id=service_id
    )

    await callback.message.answer(
        "🔗 Send Instagram Link"
    )

    await state.set_state(
        OrderState.waiting_link
    )


# ==========================================
# GET LINK
# ==========================================

@router.message(OrderState.waiting_link)
async def get_link(
    message: Message,
    state: FSMContext
):

    if message.text in [
        "💰 Deposit",
        "📸 Instagram Services",
        "🆘 Support"
    ]:
        await state.clear()
        return

    await state.update_data(
        link=message.text.strip()
    )

    await message.answer(
        "📦 Send Quantity"
    )

    await state.set_state(
        OrderState.waiting_quantity
    )


# ==========================================
# GET QUANTITY + PLACE ORDER
# ==========================================

@router.message(OrderState.waiting_quantity)
async def get_quantity(
    message: Message,
    state: FSMContext
):

    if message.text in [
        "💰 Deposit",
        "📸 Instagram Services",
        "🆘 Support"
    ]:
        await state.clear()
        return

    if not message.text.isdigit():
        return await message.answer(
            "❌ Quantity must be a number"
        )

    quantity = int(message.text)

    data = await state.get_data()

    service_id = data["service_id"]
    link = data["link"]

    db = await connect()

    cur = await db.execute(
        """
        SELECT name,price,min_q,max_q
        FROM services
        WHERE id=?
        """,
        (service_id,)
    )

    service = await cur.fetchone()

    if not service:
        await db.close()
        return await message.answer(
            "❌ Service not found"
        )

    name, price, min_q, max_q = service

    if quantity < min_q:

        await db.close()

        return await message.answer(
            f"❌ Minimum Quantity: {min_q}"
        )

    if quantity > max_q:

        await db.close()

        return await message.answer(
            f"❌ Maximum Quantity: {max_q}"
        )

    total_price = round(
        (quantity / 1000) * price,
        2
    )

    cur = await db.execute(
        """
        SELECT balance
        FROM users
        WHERE user_id=?
        """,
        (message.from_user.id,)
    )

    user = await cur.fetchone()

    if not user:

        await db.close()

        return await message.answer(
            "❌ User not found"
        )

    balance = user[0]

    if balance < total_price:

        await db.close()

        return await message.answer(
            f"""
❌ Insufficient Balance

Required: ₹{total_price}
Available: ₹{balance}
"""
        )

    # ==========================================
    # PLACE API ORDER
    # ==========================================

    provider_order_id = "PENDING"

    try:

        payload = {
            "key": API_KEY,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity
        }

        if API_URL and API_KEY:

            response = requests.post(
                API_URL,
                data=payload,
                timeout=30
            )

            result = response.json()

            if "order" in result:
                provider_order_id = str(
                    result["order"]
                )

            elif "order_id" in result:
                provider_order_id = str(
                    result["order_id"]
                )

            else:
                provider_order_id = "UNKNOWN"

    except Exception as e:

        await db.close()

        return await message.answer(
            f"❌ API Error\n\n{e}"
        )

    # ==========================================
    # DEDUCT BALANCE
    # ==========================================

    await db.execute(
        """
        UPDATE users
        SET balance = balance - ?
        WHERE user_id=?
        """,
        (
            total_price,
            message.from_user.id
        )
    )

    # ==========================================
    # SAVE ORDER
    # ==========================================

    await db.execute(
        """
        INSERT INTO orders
        (
            user_id,
            service_id,
            link,
            quantity,
            price,
            provider_order_id,
            status
        )
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            message.from_user.id,
            service_id,
            link,
            quantity,
            total_price,
            provider_order_id,
            "Processing"
        )
    )

    await db.commit()

    cur = await db.execute(
        "SELECT last_insert_rowid()"
    )

    order_id = (
        await cur.fetchone()
    )[0]

    await db.close()

    # ==========================================
    # SUCCESS
    # ==========================================

    await message.answer(
        f"""
✅ Order Created Successfully

🆔 Order ID: {order_id}

📦 Service:
{name}

🔢 Quantity:
{quantity}

💰 Cost:
₹{total_price}

📊 Status:
Processing

🛰 Provider ID:
{provider_order_id}
"""
    )

    await state.clear()