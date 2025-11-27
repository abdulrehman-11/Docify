"""
Script to link existing calendar events with database appointments.
Matches by patient name and appointment time.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add paths
backend_dir = Path(__file__).parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from sqlalchemy import select
from api_database import AsyncSessionLocal
from models.appointment import Appointment, AppointmentStatus
from models.patient import Patient
from services.google_calendar_service import get_calendar_service
from dateutil import parser as date_parser

async def link_calendar_events():
    """Link existing calendar events to database appointments."""
    print("=== Linking Calendar Events to Database Appointments ===\n")
    
    # Initialize calendar
    calendar = get_calendar_service()
    calendar.initialize()
    
    if not calendar._initialized:
        print("❌ Calendar not initialized!")
        return
    
    print(f"✅ Calendar initialized: {calendar.calendar_id}\n")
    
    # Get all calendar events (past and future)
    past_date = datetime.now(timezone.utc) - timedelta(days=30)
    events_response = calendar.service.events().list(
        calendarId=calendar.calendar_id,
        timeMin=past_date.isoformat(),
        maxResults=250,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    all_events = events_response.get('items', [])
    
    # Filter to only Hexaa Clinic events
    clinic_events = [e for e in all_events if e.get('summary', '').startswith('Hexaa Clinic')]
    print(f"Found {len(clinic_events)} Hexaa Clinic events in calendar\n")
    
    # Build lookup by patient name from summary
    events_by_patient = {}
    for event in clinic_events:
        summary = event.get('summary', '')
        # Extract patient name from "Hexaa Clinic - Patient Name"
        if ' - ' in summary:
            patient_name = summary.split(' - ', 1)[1]
            start_str = event.get('start', {}).get('dateTime')
            if start_str:
                start_time = date_parser.parse(start_str)
                key = (patient_name.lower().strip(), start_time.replace(tzinfo=None))
                events_by_patient[key] = event
    
    print(f"Parsed {len(events_by_patient)} events with patient names\n")
    
    async with AsyncSessionLocal() as session:
        # Get all appointments without calendar IDs
        stmt = select(Appointment, Patient).join(
            Patient, Appointment.patient_id == Patient.id
        ).where(
            Appointment.google_calendar_event_id.is_(None),
            Appointment.status.in_([AppointmentStatus.CONFIRMED, AppointmentStatus.COMPLETED])
        )
        
        result = await session.execute(stmt)
        rows = result.all()
        
        print(f"Found {len(rows)} appointments without calendar IDs\n")
        
        linked = 0
        created = 0
        
        for appointment, patient in rows:
            # Try to find matching calendar event
            db_time = appointment.start_time.replace(tzinfo=None)
            
            # Convert to PKT for comparison (UTC+5)
            pkt_time = db_time + timedelta(hours=5)
            
            key = (patient.name.lower().strip(), pkt_time)
            
            if key in events_by_patient:
                event = events_by_patient[key]
                event_id = event.get('id')
                appointment.google_calendar_event_id = event_id
                linked += 1
                print(f"✅ Linked: Appointment {appointment.id} ({patient.name}) -> Event {event_id[:20]}...")
            else:
                # Try without timezone conversion
                key2 = (patient.name.lower().strip(), db_time)
                if key2 in events_by_patient:
                    event = events_by_patient[key2]
                    event_id = event.get('id')
                    appointment.google_calendar_event_id = event_id
                    linked += 1
                    print(f"✅ Linked: Appointment {appointment.id} ({patient.name}) -> Event {event_id[:20]}...")
                else:
                    # Create new calendar event
                    print(f"⚠️  No match found for: Appointment {appointment.id} ({patient.name}, {db_time})")
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
                        created += 1
                        print(f"   ✅ Created new event: {event_id[:20]}...")
        
        await session.commit()
        
        print(f"\n=== Summary ===")
        print(f"Linked to existing events: {linked}")
        print(f"Created new events: {created}")
        print(f"Total synced: {linked + created}")


if __name__ == "__main__":
    asyncio.run(link_calendar_events())
