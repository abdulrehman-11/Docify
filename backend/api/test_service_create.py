"""Test appointment creation with calendar through the service."""
import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add paths
backend_dir = Path(__file__).parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from api_database import AsyncSessionLocal
from api_services.appointment_service import AppointmentAPIService, CALENDAR_AVAILABLE, get_calendar_service

async def test_create():
    print("=== Testing Appointment Creation with Calendar ===\n")
    print(f"CALENDAR_AVAILABLE: {CALENDAR_AVAILABLE}")
    
    if CALENDAR_AVAILABLE:
        cal_svc = get_calendar_service()
        cal_svc.initialize()
        print(f"Calendar initialized: {cal_svc._initialized}")
        print(f"Calendar service: {cal_svc.service is not None}")
    
    async with AsyncSessionLocal() as session:
        service = AppointmentAPIService(session)
        
        start = datetime.now() + timedelta(days=20)
        end = start + timedelta(minutes=30)
        
        print(f"\nCreating appointment...")
        print(f"  Patient ID: 1")
        print(f"  Start: {start}")
        print(f"  End: {end}")
        
        try:
            appointment = await service.create_appointment(
                patient_id=1,
                start_time=start,
                end_time=end,
                reason="Test via service"
            )
            await session.commit()
            
            print(f"\n✅ Appointment created!")
            print(f"  ID: {appointment.id}")
            print(f"  Calendar Event ID: {appointment.google_calendar_event_id}")
            
            if appointment.google_calendar_event_id:
                print("  ✅ Calendar sync successful!")
            else:
                print("  ❌ Calendar event NOT created!")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_create())
