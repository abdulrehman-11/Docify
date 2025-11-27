"""Test calendar connection and list events."""
import sys
sys.path.insert(0, '../agent-python')

from services.google_calendar_service import get_calendar_service
from datetime import datetime, timezone

cs = get_calendar_service()
cs.initialize()

print("=== Google Calendar Test ===\n")
print(f"Calendar ID: {cs.calendar_id}")
print(f"Initialized: {cs._initialized}")

# List events
events = cs.service.events().list(
    calendarId=cs.calendar_id,
    timeMin=datetime.now(timezone.utc).isoformat(),
    maxResults=20,
    singleEvents=True,
    orderBy='startTime'
).execute()

print(f"\nUpcoming Events ({len(events.get('items', []))}):")
for e in events.get('items', []):
    print(f"  - {e.get('summary', 'No title')}")
    print(f"    Start: {e.get('start', {}).get('dateTime')}")
    print(f"    ID: {e.get('id')}")
    print()
