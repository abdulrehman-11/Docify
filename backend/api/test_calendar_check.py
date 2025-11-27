"""Quick check of calendar and DB connection."""
import asyncio
import sys
from pathlib import Path

# Add agent-python to path
backend_dir = Path(__file__).parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from api_database import engine
from sqlalchemy import text

async def check():
    print("=== Checking Database Appointments (Recent First) ===")
    async with engine.connect() as conn:
        # Get recent appointments ordered by creation date
        result = await conn.execute(text(
            "SELECT id, patient_id, start_time, status, google_calendar_event_id, created_at "
            "FROM appointments ORDER BY created_at DESC LIMIT 15"
        ))
        rows = result.fetchall()
        print(f"Found {len(rows)} recent appointments:")
        for r in rows:
            cal_id = r[4] if r[4] else "NO CALENDAR ID"
            print(f"  ID={r[0]}, patient={r[1]}, time={r[2]}, status={r[3]}, created={r[5]}")
            print(f"      calendar_id={cal_id}")
    
    print("\n=== Checking Google Calendar ===")
    from services.google_calendar_service import get_calendar_service
    from datetime import datetime as dt, timezone as tz
    svc = get_calendar_service()
    svc.initialize()
    print(f"Calendar initialized: {svc._initialized}")
    print(f"Calendar ID: {svc.calendar_id}")
    
    if svc._initialized and svc.service:
        events = svc.service.events().list(
            calendarId=svc.calendar_id, 
            timeMin=dt.now(tz.utc).isoformat(),
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        items = events.get('items', [])
        print(f"Found {len(items)} FUTURE events:")
        for e in items:
            start = e.get('start', {}).get('dateTime', e.get('start', {}).get('date'))
            print(f"  {e.get('summary')} - {start}")

if __name__ == "__main__":
    asyncio.run(check())
