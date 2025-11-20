"""
Test script to verify API setup and database connection.
"""
import asyncio
import sys
from pathlib import Path

# Add agent-python to path
backend_dir = Path(__file__).parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))
sys.path.insert(0, str(Path(__file__).parent))

async def test_database_connection():
    """Test database connection."""
    print("🔍 Testing database connection...")
    
    try:
        from database import engine, AsyncSessionLocal
        from models.patient import Patient
        from models.appointment import Appointment
        from models.clinic_hours import ClinicHours
        from sqlalchemy import select, text
        
        # Test connection with a simple query
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        # Test session creation
        async with AsyncSessionLocal() as session:
            # Check if tables exist
            result = await session.execute(select(Patient).limit(1))
            print("✅ Patients table accessible!")
            
            result = await session.execute(select(Appointment).limit(1))
            print("✅ Appointments table accessible!")
            
            result = await session.execute(select(ClinicHours))
            hours = result.scalars().all()
            print(f"✅ Clinic hours table accessible! Found {len(hours)} days configured")
        
        print("\n✨ All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_services():
    """Test service methods."""
    print("\n🔍 Testing service methods...")
    
    try:
        from database import AsyncSessionLocal
        from services.patient_service import PatientAPIService
        from services.appointment_service import AppointmentAPIService
        
        async with AsyncSessionLocal() as session:
            # Test patient service
            patient_service = PatientAPIService(session)
            patients, total = await patient_service.get_all_patients(skip=0, limit=5)
            print(f"✅ Patient service working! Found {total} total patients")
            
            # Test appointment service
            appointment_service = AppointmentAPIService(session)
            stats = await appointment_service.get_appointment_stats()
            print(f"✅ Appointment service working! Stats: {stats}")
        
        print("\n✨ All service tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 ETHER CLINIC API - SYSTEM TEST")
    print("=" * 60)
    
    db_ok = await test_database_connection()
    if not db_ok:
        print("\n❌ Database tests failed. Please check your connection.")
        return False
    
    services_ok = await test_services()
    if not services_ok:
        print("\n❌ Service tests failed.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! API is ready to start.")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("  1. Run the API: python main.py")
    print("  2. Visit docs: http://localhost:8000/docs")
    print("  3. Test endpoints in the interactive documentation")
    
    return True


if __name__ == "__main__":
    asyncio.run(main())
