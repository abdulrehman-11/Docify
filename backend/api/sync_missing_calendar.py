"""Sync appointments missing calendar events."""
import asyncio
import sys
from pathlib import Path

# Add agent-python to path
backend_dir = Path(__file__).parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from sqlalchemy import select
from api_database import AsyncSessionLocal
from models.appointment import Appointment, AppointmentStatus
from models.patient import Patient
from services.google_calendar_service import get_calendar_service

async def sync_missing():
    print("=== Syncing Appointments Missing Calendar Events ===\n")
    
    # Initialize calendar
    calendar = get_calendar_service()
    calendar.initialize()
    
    if not calendar._initialized:
        print("❌ Calendar not initialized!")
        return
    
    print(f"✅ Calendar initialized: {calendar.calendar_id}\n")
    
    async with AsyncSessionLocal() as session:
        # Find appointments without calendar events
        stmt = select(Appointment, Patient).join(
            Patient, Appointment.patient_id == Patient.id
        ).where(
            Appointment.google_calendar_event_id.is_(None),
            Appointment.status == AppointmentStatus.CONFIRMED
        )
        
        result = await session.execute(stmt)
        rows = result.all()
        
        print(f"Found {len(rows)} appointments without calendar events:\n")
        
        for appointment, patient in rows:
            print(f"  ID={appointment.id}, Patient={patient.name}, Time={appointment.start_time}")
            
            # Create calendar event
            event_id = calendar.create_event(
                patient_name=patient.name,
                patient_email=patient.email,
                patient_phone=patient.phone,
                reason=appointment.reason or "Appointment",
                start_time=appointment.start_time,
                end_time=appointment.end_time,
                appointment_id=appointment.id
            )
            
            if event_id:
                appointment.google_calendar_event_id = event_id
                print(f"      ✅ Created calendar event: {event_id}")
            else:
                print(f"      ❌ Failed to create calendar event")
        
        await session.commit()
        print(f"\n✅ Done! Synced {len(rows)} appointments to calendar.")

if __name__ == "__main__":
    asyncio.run(sync_missing())
