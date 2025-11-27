"""Test Google Calendar event creation directly."""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add agent-python to path
backend_dir = Path(__file__).parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from services.google_calendar_service import get_calendar_service

print("=== Testing Google Calendar Event Creation ===\n")

# Get service
calendar_service = get_calendar_service()
print(f"1. Calendar service obtained: {calendar_service is not None}")

# Initialize
init_result = calendar_service.initialize()
print(f"2. Initialization result: {init_result}")
print(f"3. Service initialized: {calendar_service._initialized}")
print(f"4. Service object: {calendar_service.service is not None}")
print(f"5. Calendar ID: {calendar_service.calendar_id}")

if calendar_service._initialized and calendar_service.service:
    # Try creating an event
    start = datetime.now() + timedelta(days=10)
    end = start + timedelta(minutes=30)
    
    print(f"\n6. Creating test event...")
    print(f"   Start: {start}")
    print(f"   End: {end}")
    
    event_id = calendar_service.create_event(
        patient_name="Test Patient",
        patient_email="test@example.com",
        patient_phone="+92-300-1234567",
        reason="Test Calendar Creation",
        start_time=start,
        end_time=end,
        appointment_id=99999
    )
    
    if event_id:
        print(f"\n✅ SUCCESS! Event created with ID: {event_id}")
        
        # Verify it exists
        try:
            event = calendar_service.service.events().get(
                calendarId=calendar_service.calendar_id,
                eventId=event_id
            ).execute()
            print(f"   Event verified: {event.get('summary')}")
            print(f"   Event link: {event.get('htmlLink')}")
            
            # Delete the test event
            calendar_service.service.events().delete(
                calendarId=calendar_service.calendar_id,
                eventId=event_id
            ).execute()
            print(f"   Test event deleted ✓")
        except Exception as e:
            print(f"   Verification error: {e}")
    else:
        print("\n❌ FAILED! No event ID returned")
else:
    print("\n❌ Calendar service not properly initialized")
