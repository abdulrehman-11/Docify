"""Test timezone handling"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add agent-python to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent / "agent-python"))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv
import pytz

load_dotenv('.env.local')

KARACHI_TZ = pytz.timezone("Asia/Karachi")

async def check_db_times():
    engine = create_async_engine(os.getenv('DATABASE_URL'))
    
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT id, start_time, end_time, 
                   pg_typeof(start_time) as type
            FROM appointments 
            ORDER BY id DESC
            LIMIT 5
        """))
        rows = result.fetchall()
        
        print("\n=== DB TIMES (raw from PostgreSQL) ===")
        for r in rows:
            utc_time = r[1]
            # Convert to Karachi time
            if utc_time.tzinfo is None:
                utc_time = utc_time.replace(tzinfo=timezone.utc)
            karachi_time = utc_time.astimezone(KARACHI_TZ)
            
            print(f"ID: {r[0]}")
            print(f"   DB (UTC):      {r[1]}")
            print(f"   Karachi Time:  {karachi_time}")
            print(f"   For Calendar:  {karachi_time.isoformat()}")
            print()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_db_times())
