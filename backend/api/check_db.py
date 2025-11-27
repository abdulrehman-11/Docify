"""Check appointments in database."""
import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from sqlalchemy import select
from api_database import AsyncSessionLocal
from models.appointment import Appointment, AppointmentStatus
from models.patient import Patient

async def check_db():
    async with AsyncSessionLocal() as session:
        stmt = select(Appointment, Patient).join(
            Patient, Appointment.patient_id == Patient.id
        ).order_by(Appointment.start_time.desc()).limit(10)
        
        result = await session.execute(stmt)
        rows = result.all()
        
        print("=== Database Appointments ===\n")
        for apt, patient in rows:
            cal_id = apt.google_calendar_event_id or "NONE"
            if cal_id != "NONE":
                cal_id = cal_id[:25] + "..."
            print(f"ID={apt.id}, Patient={patient.name}, Status={apt.status.value}")
            print(f"  Time: {apt.start_time}")
            print(f"  Calendar ID: {cal_id}")
            print()

if __name__ == "__main__":
    asyncio.run(check_db())
