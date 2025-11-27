"""Fix database schema - make extra columns nullable."""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv('.env.local')

async def fix_schema():
    engine = create_async_engine(os.getenv('DATABASE_URL'))
    
    print("\n=== Fixing Database Schema ===\n")
    
    async with engine.begin() as conn:
        # Make the extra columns nullable
        await conn.execute(text("""
            ALTER TABLE appointments ALTER COLUMN name DROP NOT NULL;
        """))
        print("  ✅ Made 'name' nullable")
        
        await conn.execute(text("""
            ALTER TABLE appointments ALTER COLUMN email DROP NOT NULL;
        """))
        print("  ✅ Made 'email' nullable")
        
        await conn.execute(text("""
            ALTER TABLE appointments ALTER COLUMN phone DROP NOT NULL;
        """))
        print("  ✅ Made 'phone' nullable")
        
        await conn.execute(text("""
            ALTER TABLE appointments ALTER COLUMN date DROP NOT NULL;
        """))
        print("  ✅ Made 'date' nullable")
        
        await conn.execute(text("""
            ALTER TABLE appointments ALTER COLUMN day DROP NOT NULL;
        """))
        print("  ✅ Made 'day' nullable")
        
        await conn.execute(text("""
            ALTER TABLE appointments ALTER COLUMN time DROP NOT NULL;
        """))
        print("  ✅ Made 'time' nullable")
    
    print("\n✅ Schema fixed! Appointments can now be created.\n")
    await engine.dispose()

asyncio.run(fix_schema())
