import asyncio
import aiosqlite

DB_NAME = "data/smm.db"

services = [
    (
        10695,
        "Instagram",
        "👁 Instagram Reel Views",
        1,
        100,
        100000000
    ),

    (
        13914,
        "Instagram",
        "❤️ Instagram Likes",
        8,
        10,
        1000000
    ),

    (
        12287,
        "Instagram",
        "📤 Instagram Shares",
        3,
        10,
        1000000
    ),

    (
        13541,
        "Instagram",
        "👥 Instagram Followers",
        50,
        100,
        1000000
    )
]

async def main():

    db = await aiosqlite.connect(DB_NAME)

    await db.execute("DELETE FROM services")

    for service in services:

        await db.execute(
            """
            INSERT INTO services
            (
                id,
                category,
                name,
                price,
                min_q,
                max_q
            )
            VALUES(?,?,?,?,?,?)
            """,
            service
        )

    await db.commit()
    await db.close()

    print("Services Imported Successfully")

asyncio.run(main())