import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import create_tables

# Routers
from handlers.start import router as start_router
from handlers.categories import router as categories_router
from handlers.orders import router as orders_router
from handlers.recharge import router as recharge_router
from handlers.admin import router as admin_router

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()


async def main():

    # Create database tables
    await create_tables()

    # Register routers
    dp.include_router(start_router)
    dp.include_router(categories_router)
    dp.include_router(orders_router)
    dp.include_router(recharge_router)
    dp.include_router(admin_router)

    # Clear pending updates
    await bot.delete_webhook(
        drop_pending_updates=True
    )

    print("================================")
    print("   Alkot SMM Bot Started")
    print("================================")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())