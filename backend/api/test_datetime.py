"""
Test script to check datetime serialization from database
"""
import asyncio
from datetime import datetime, timezone
from api_database import AsyncSessionLocal
from sqlalchemy import select, text
import sys

async def test_datetime_from_db():
    """Query database and show actual datetime values"""
    print("=" * 60)
    print("TESTING DATETIME FROM DATABASE")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        # Get raw data using text query
        result = await session.execute(
            text("SELECT id, start_time, end_time, status FROM appointments LIMIT 3")
        )
        rows = result.fetchall()
        
        print("\n📊 Raw Database Query Results:")
        print("-" * 60)
        for row in rows:
            print(f"\nID: {row[0]}")
            print(f"  Start Time: {row[1]}")
            print(f"  Type: {type(row[1])}")
            print(f"  Has tzinfo: {row[1].tzinfo if hasattr(row[1], 'tzinfo') else 'N/A'}")
            print(f"  ISO format: {row[1].isoformat() if hasattr(row[1], 'isoformat') else 'N/A'}")
            print(f"  Status: {row[3]}")
        
        # Now test with ORM models
        print("\n" + "=" * 60)
        print("TESTING WITH ORM MODELS")
        print("=" * 60)
        
        from models.appointment import Appointment
        
        result = await session.execute(
            select(Appointment).limit(3)
        )
        appointments = result.scalars().all()
        
        print("\n📦 ORM Model Results:")
        print("-" * 60)
        for apt in appointments:
            print(f"\nID: {apt.id}")
            print(f"  Start Time: {apt.start_time}")
            print(f"  Type: {type(apt.start_time)}")
            print(f"  Has tzinfo: {apt.start_time.tzinfo}")
            print(f"  ISO format: {apt.start_time.isoformat()}")
            
            # Test the serializer
            if apt.start_time.tzinfo is None:
                print(f"  ⚠️  WARNING: Datetime is timezone-naive!")
                aware = apt.start_time.replace(tzinfo=timezone.utc)
                print(f"  After adding UTC: {aware.isoformat()}")
            else:
                print(f"  ✅ Datetime is timezone-aware")
        
        # Test API schema serialization
        print("\n" + "=" * 60)
        print("TESTING API SCHEMA SERIALIZATION")
        print("=" * 60)
        
        from api_schemas.appointment import AppointmentWithPatientResponse
        from models.patient import Patient
        
        # Get an appointment with patient
        result = await session.execute(
            select(Appointment).limit(1)
        )
        apt = result.scalar_one()
        
        # Get patient info
        patient_result = await session.execute(
            select(Patient).where(Patient.id == apt.patient_id)
        )
        patient = patient_result.scalar_one()
        
        # Create response object
        response_data = {
            'id': apt.id,
            'patient_id': apt.patient_id,
            'patient_name': patient.name,
            'patient_email': patient.email,
            'patient_phone': patient.phone,
            'start_time': apt.start_time,
            'end_time': apt.end_time,
            'reason': apt.reason,
            'status': apt.status.value,
            'cancellation_reason': apt.cancellation_reason,
            'created_at': apt.created_at,
            'updated_at': apt.updated_at,
        }
        
        response = AppointmentWithPatientResponse(**response_data)
        
        print("\n📤 Serialized API Response:")
        print("-" * 60)
        print(f"Response dict: {response.model_dump()}")
        print(f"\nJSON output: {response.model_dump_json()}")
        
        import json
        parsed = json.loads(response.model_dump_json())
        print(f"\n🔍 Start time in JSON: {parsed['start_time']}")
        print(f"   Type: {type(parsed['start_time'])}")

if __name__ == "__main__":
    asyncio.run(test_datetime_from_db())
