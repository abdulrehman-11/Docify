"""Verify database schema after migration"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_Zysz7qvmUwF3@ep-purple-paper-a4mvi7w9-pooler.us-east-1.aws.neon.tech/neondb?ssl=require"

async def verify():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        # Check clinic_hours columns
        result = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'clinic_hours' ORDER BY ordinal_position"
        ))
        print("✅ clinic_hours table columns:")
        for row in result:
            print(f"   - {row[0]}")
        
        # Check clinic_holidays table exists
        result2 = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'clinic_holidays' ORDER BY ordinal_position"
        ))
        rows = result2.fetchall()
        if rows:
            print("\n✅ clinic_holidays table columns:")
            for row in rows:
                print(f"   - {row[0]}")
        else:
            print("\n❌ clinic_holidays table not found!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify())
