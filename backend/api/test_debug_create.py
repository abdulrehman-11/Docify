"""Test creating an appointment directly to find the issue."""
import asyncio
import sys
from pathlib import Path

# Add agent-python to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agent-python"))

from dotenv import load_dotenv
load_dotenv('.env.local')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import os
from datetime import datetime, timezone

from models.appointment import Appointment, AppointmentStatus
from models.patient import Patient

DATABASE_URL = os.getenv("DATABASE_URL")

async def test_create():
    print("\n=== Testing Appointment Creation ===\n")
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get first patient
        patient_result = await session.execute(select(Patient).limit(1))
        patient = patient_result.scalar_one_or_none()
        
        if not patient:
            print("No patient found!")
            return
        
        print(f"Using patient: {patient.name} (ID: {patient.id})")
        
        # Create appointment
        start_time = datetime(2025, 11, 28, 15, 0, 0, tzinfo=timezone.utc)
        end_time = datetime(2025, 11, 28, 15, 30, 0, tzinfo=timezone.utc)
        
        print(f"\nCreating appointment:")
        print(f"  Start: {start_time}")
        print(f"  End: {end_time}")
        
        try:
            appointment = Appointment(
                patient_id=patient.id,
                start_time=start_time,
                end_time=end_time,
                reason="Test from debug script",
                status=AppointmentStatus.CONFIRMED
            )
            session.add(appointment)
            await session.commit()
            await session.refresh(appointment)
            
            print(f"\n✅ Created appointment ID: {appointment.id}")
            print(f"   Start: {appointment.start_time}")
            print(f"   End: {appointment.end_time}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_create())
