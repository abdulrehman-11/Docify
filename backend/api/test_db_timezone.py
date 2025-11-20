"""Test database timezone and appointment retrieval"""
import sys
from pathlib import Path

# Add agent-python to path
backend_dir = Path(__file__).parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

import asyncio
from sqlalchemy import text
from api_database import engine, AsyncSessionLocal
from models.appointment import Appointment
from models.patient import Patient
from datetime import datetime, timezone

async def test_db_timezone():
    """Test database timezone settings"""
    print("=" * 80)
    print("TESTING DATABASE TIMEZONE")
    print("=" * 80)
    
    async with engine.begin() as conn:
        # Check database timezone
        result = await conn.execute(text("SHOW timezone"))
        db_tz = result.scalar()
        print(f"\n📍 Database timezone setting: {db_tz}")
        
        # Check current times
        result = await conn.execute(text(
            "SELECT NOW() as local_time, NOW() AT TIME ZONE 'UTC' as utc_time, CURRENT_TIMESTAMP as current_ts"
        ))
        row = result.fetchone()
        print(f"🕐 Database NOW(): {row[0]}")
        print(f"🌍 Database UTC time: {row[1]}")
        print(f"⏰ Database CURRENT_TIMESTAMP: {row[2]}")
        
        # Check Python timezone
        now_utc = datetime.now(timezone.utc)
        now_local = datetime.now()
        print(f"\n🐍 Python UTC time: {now_utc}")
        print(f"📍 Python local time: {now_local}")
        print(f"⏰ Timezone offset: {now_local.astimezone().utcoffset()}")

async def test_appointment_retrieval():
    """Test how appointments are stored and retrieved"""
    print("\n" + "=" * 80)
    print("TESTING APPOINTMENT RETRIEVAL")
    print("=" * 80)
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        
        # Get first few appointments with patient info
        stmt = select(Appointment, Patient).join(
            Patient, Appointment.patient_id == Patient.id
        ).limit(5).order_by(Appointment.start_time.desc())
        
        result = await session.execute(stmt)
        rows = result.all()
        
        print(f"\n📋 Found {len(rows)} appointments:")
        for i, (apt, patient) in enumerate(rows, 1):
            print(f"\n--- Appointment {i} ---")
            print(f"ID: {apt.id}")
            print(f"Patient: {patient.name}")
            print(f"Start Time (DB): {apt.start_time}")
            print(f"Start Time Type: {type(apt.start_time)}")
            print(f"Start Time TZ Info: {apt.start_time.tzinfo if hasattr(apt.start_time, 'tzinfo') else 'N/A'}")
            print(f"End Time (DB): {apt.end_time}")
            print(f"Reason: {apt.reason}")
            print(f"Status: {apt.status.value}")
            
            # Check how it would be serialized
            if apt.start_time.tzinfo is None:
                print("⚠️  WARNING: Datetime is timezone-naive!")
                # If naive, assume UTC
                aware_dt = apt.start_time.replace(tzinfo=timezone.utc)
                print(f"   After adding UTC: {aware_dt.isoformat()}")
            else:
                print(f"✅ Datetime is timezone-aware: {apt.start_time.isoformat()}")

async def test_appointment_creation():
    """Test creating an appointment with explicit timezone"""
    print("\n" + "=" * 80)
    print("TESTING APPOINTMENT CREATION")
    print("=" * 80)
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        
        # Get first patient
        stmt = select(Patient).limit(1)
        result = await session.execute(stmt)
        patient = result.scalar_one_or_none()
        
        if not patient:
            print("❌ No patients found to test with")
            return
        
        print(f"\n🧪 Creating test appointment for patient: {patient.name}")
        
        # Create appointment with timezone-aware datetime
        from datetime import timedelta
        now_utc = datetime.now(timezone.utc)
        start_time = now_utc + timedelta(days=1, hours=2)
        end_time = start_time + timedelta(hours=1)
        
        print(f"📅 Start time (UTC aware): {start_time}")
        print(f"📅 Start time ISO: {start_time.isoformat()}")
        print(f"📅 End time (UTC aware): {end_time}")
        
        new_apt = Appointment(
            patient_id=patient.id,
            start_time=start_time,
            end_time=end_time,
            reason="Test timezone handling"
        )
        
        session.add(new_apt)
        await session.flush()
        
        print(f"\n✅ Created appointment ID: {new_apt.id}")
        print(f"   Start time stored: {new_apt.start_time}")
        print(f"   Start time type: {type(new_apt.start_time)}")
        print(f"   TZ info: {new_apt.start_time.tzinfo}")
        
        # Rollback - don't actually save test data
        await session.rollback()
        print("\n🔄 Rolled back test appointment (not saved)")

async def main():
    try:
        await test_db_timezone()
        await test_appointment_retrieval()
        await test_appointment_creation()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
