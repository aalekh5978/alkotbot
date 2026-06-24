import aiosqlite

DB_NAME = "data/smm.db"


async def connect():
    return await aiosqlite.connect(DB_NAME)


async def create_tables():

    db = await connect()

    await db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance REAL DEFAULT 0
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS services(
        id INTEGER PRIMARY KEY,
        category TEXT,
        name TEXT,
        price REAL,
        min_q INTEGER,
        max_q INTEGER
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        service_id INTEGER,
        link TEXT,
        quantity INTEGER,
        price REAL,
        provider_order_id TEXT,
        status TEXT
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS deposits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        screenshot_file_id TEXT,
        amount REAL DEFAULT 0,
        status TEXT DEFAULT 'Pending'
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY,
        upi_id TEXT,
        qr_file_id TEXT
    )
    """)

    cur = await db.execute(
        "SELECT id FROM settings WHERE id=1"
    )

    exists = await cur.fetchone()

    if not exists:
        await db.execute(
            """
            INSERT INTO settings
            (
                id,
                upi_id,
                qr_file_id
            )
            VALUES
            (
                1,
                '',
                ''
            )
            """
        )

    await db.commit()
    await db.close()