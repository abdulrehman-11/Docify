"""
Re-sync all calendar events with correct timezone.
This will:
1. Delete all existing calendar events
2. Clear google_calendar_event_id from database
3. Re-create events with correct local time
"""
import asyncio
import sys
import os
from pathlib import Path

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Add agent-python to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent / "agent-python"))

from dotenv import load_dotenv
load_dotenv(".env.local")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update

# Import models and services
from models.appointment import Appointment, AppointmentStatus
from models.patient import Patient
from services.google_calendar_service import get_calendar_service

DATABASE_URL = os.getenv("DATABASE_URL")

async def resync_calendar():
    """Delete old events and resync with correct timezone."""
    
    print("=" * 60)
    print("🔄 Re-syncing Calendar Events with Correct Timezone")
    print("=" * 60)
    
    # Create database connection
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Initialize calendar service
    calendar_service = get_calendar_service()
    if not calendar_service.initialize():
        print("❌ Failed to initialize Google Calendar service")
        return
    
    print(f"✅ Connected to calendar: {calendar_service.calendar_id}")
    
    async with async_session() as session:
        # Step 1: Get all appointments with calendar event IDs
        print("\n📋 Step 1: Finding existing calendar events...")
        
        stmt = select(Appointment).where(
            Appointment.google_calendar_event_id != None,
            Appointment.google_calendar_event_id != ""
        )
        result = await session.execute(stmt)
        appointments_with_events = result.scalars().all()
        
        print(f"   Found {len(appointments_with_events)} events to delete")
        
        # Step 2: Delete calendar events
        print("\n🗑️  Step 2: Deleting old calendar events...")
        deleted = 0
        for apt in appointments_with_events:
            try:
                if calendar_service.delete_event(apt.google_calendar_event_id):
                    print(f"   ✅ Deleted event {apt.google_calendar_event_id}")
                    deleted += 1
                else:
                    print(f"   ⚠️  Could not delete {apt.google_calendar_event_id}")
            except Exception as e:
                print(f"   ❌ Error deleting {apt.google_calendar_event_id}: {e}")
        
        print(f"   Deleted {deleted} events")
        
        # Step 3: Clear all calendar event IDs from database
        print("\n🧹 Step 3: Clearing calendar event IDs from database...")
        
        await session.execute(
            update(Appointment).values(google_calendar_event_id=None)
        )
        await session.commit()
        print("   ✅ Cleared all calendar event IDs")
        
        # Step 4: Re-sync all confirmed appointments
        print("\n🗓️  Step 4: Re-creating calendar events with correct timezone...")
        
        stmt = select(Appointment, Patient).join(
            Patient, Appointment.patient_id == Patient.id
        ).where(
            Appointment.status == AppointmentStatus.CONFIRMED
        ).order_by(Appointment.start_time)
        
        result = await session.execute(stmt)
        appointments = result.all()
        
        print(f"   Found {len(appointments)} confirmed appointments")
        
        synced = 0
        failed = 0
        
        for appointment, patient in appointments:
            # Show raw DB time - this is exactly what calendar will show
            raw_time = appointment.start_time.replace(tzinfo=None)
            
            print(f"\n   📅 {patient.name}")
            print(f"      DB Time:       {raw_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"      Calendar Time: {raw_time.strftime('%Y-%m-%d %H:%M')} (same)")
            
            try:
                event_id = calendar_service.create_event(
                    patient_name=patient.name,
                    patient_email=patient.email,
                    patient_phone=patient.phone,
                    reason=appointment.reason,
                    start_time=appointment.start_time,
                    end_time=appointment.end_time,
                    appointment_id=appointment.id
                )
                
                if event_id:
                    appointment.google_calendar_event_id = event_id
                    await session.commit()
                    print(f"      ✅ Created: {event_id}")
                    synced += 1
                else:
                    print(f"      ❌ Failed to create event")
                    failed += 1
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Re-sync Complete!")
        print(f"   ✅ Synced: {synced}")
        print(f"   ❌ Failed: {failed}")
        print("=" * 60)
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(resync_calendar())
