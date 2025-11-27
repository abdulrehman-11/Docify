"""
Sync existing appointments from database to Google Calendar.
Run this once to add all existing appointments to the calendar.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add agent-python to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent / "agent-python"))

from dotenv import load_dotenv
load_dotenv(".env.local")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Import models and services
from models.appointment import Appointment, AppointmentStatus
from models.patient import Patient
from services.google_calendar_service import get_calendar_service

DATABASE_URL = os.getenv("DATABASE_URL")

async def sync_appointments_to_calendar():
    """Sync all confirmed appointments to Google Calendar."""
    
    print("=" * 60)
    print("🗓️  Syncing Appointments to Google Calendar")
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
        # Get all confirmed appointments that don't have a calendar event
        stmt = select(Appointment, Patient).join(
            Patient, Appointment.patient_id == Patient.id
        ).where(
            Appointment.status == AppointmentStatus.CONFIRMED,
            # Only sync appointments without calendar event ID
            (Appointment.google_calendar_event_id == None) | (Appointment.google_calendar_event_id == "")
        ).order_by(Appointment.start_time)
        
        result = await session.execute(stmt)
        appointments = result.all()
        
        print(f"\n📋 Found {len(appointments)} appointments to sync\n")
        
        synced = 0
        failed = 0
        
        for appointment, patient in appointments:
            print(f"  Syncing: {patient.name} - {appointment.start_time.strftime('%Y-%m-%d %H:%M')}")
            
            try:
                # Create calendar event
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
                    # Update appointment with calendar event ID
                    appointment.google_calendar_event_id = event_id
                    await session.commit()
                    print(f"    ✅ Created event: {event_id}")
                    synced += 1
                else:
                    print(f"    ❌ Failed to create event")
                    failed += 1
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Sync Complete!")
        print(f"   ✅ Synced: {synced}")
        print(f"   ❌ Failed: {failed}")
        print("=" * 60)
        
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(sync_appointments_to_calendar())
