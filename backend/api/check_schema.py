"""Check database schema."""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv('.env.local')

async def check_schema():
    engine = create_async_engine(os.getenv('DATABASE_URL'))
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT column_name, is_nullable, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'appointments' 
            ORDER BY ordinal_position
        """))
        rows = result.fetchall()
        
        print("\n=== Appointments Table Schema ===\n")
        for row in rows:
            print(f"  {row[0]:30} | {row[1]:3} | {row[2]}")
    
    await engine.dispose()

asyncio.run(check_schema())
