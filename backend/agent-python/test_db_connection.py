"""
Test database connection for agent-python service
Run this to verify your Neon database is accessible
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Load environment variables
load_dotenv(".env.local")

async def test_connection():
    """Test database connection and list tables"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment!")
        return
    
    print("="*70)
    print("🔍 DATABASE CONNECTION TEST")
    print("="*70)
    
    # Hide password in output
    from urllib.parse import urlparse
    parsed = urlparse(database_url)
    safe_url = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}{parsed.path}"
    print(f"\n📍 Database URL: {safe_url}")
    
    try:
        # Create engine
        print("\n🔌 Creating database engine...")
        engine = create_async_engine(database_url, echo=False)
        
        # Test connection
        print("🔗 Testing connection...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected successfully!")
            print(f"📊 PostgreSQL Version: {version}")
            
            # List tables
            print("\n📋 Checking tables...")
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("⚠️  No tables found - database might not be initialized")
            
            # Count appointments
            try:
                result = await conn.execute(text("SELECT COUNT(*) FROM appointments"))
                count = result.scalar()
                print(f"\n📅 Total appointments in database: {count}")
            except Exception as e:
                print(f"⚠️  Could not count appointments: {e}")
        
        await engine.dispose()
        print("\n✅ All tests passed!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"Error: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check DATABASE_URL format")
        print("   2. Verify database credentials")
        print("   3. Ensure SSL is enabled (?ssl=require)")
        print("   4. Check firewall/network access")
        print("="*70)

if __name__ == "__main__":
    asyncio.run(test_connection())
