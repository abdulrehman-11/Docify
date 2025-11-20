"""
Test script for service layer functionality.
This script tests the PatientService and AppointmentService.
"""
import asyncio
from datetime import datetime, timedelta
from database import AsyncSessionLocal
from services import PatientService, AppointmentService
from tools.schemas import BookAppointmentInput
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_patient_service():
    """Test patient find-or-create functionality."""
    logger.info("Testing PatientService...")

    async with AsyncSessionLocal() as session:
        try:
            patient_service = PatientService(session)

            # Test creating a new patient
            test_input = BookAppointmentInput(
                name="John Doe",
                email="john.doe@example.com",
                phone="555-0100",
                reason="Annual checkup",
                slot_start="2025-11-14T10:00:00+00:00",
                slot_end="2025-11-14T10:30:00+00:00",
                insurance="Blue Cross"
            )

            patient1 = await patient_service.find_or_create_patient(test_input)
            logger.info(f"✓ Created patient: {patient1.name} (ID: {patient1.id})")

            # Test finding existing patient
            patient2 = await patient_service.find_or_create_patient(test_input)
            logger.info(f"✓ Found existing patient: {patient2.name} (ID: {patient2.id})")

            # Verify it's the same patient
            assert patient1.id == patient2.id, "Patient IDs should match"
            logger.info("✓ Patient deduplication working correctly")

            # Test get_patient_by_email
            patient3 = await patient_service.get_patient_by_email("john.doe@example.com")
            assert patient3 is not None, "Patient should be found by email"
            assert patient3.id == patient1.id, "Patient IDs should match"
            logger.info("✓ get_patient_by_email working correctly")

            await session.commit()
            logger.info("✓ PatientService tests passed!")

        except Exception as e:
            await session.rollback()
            logger.error(f"✗ PatientService test failed: {e}")
            raise

async def test_appointment_service():
    """Test appointment availability and booking functionality."""
    logger.info("Testing AppointmentService...")

    async with AsyncSessionLocal() as session:
        try:
            appointment_service = AppointmentService(session)

            # Test clinic hours retrieval
            clinic_hours = await appointment_service.get_clinic_hours(0)  # Monday
            if clinic_hours:
                logger.info(f"✓ Clinic hours for Monday: {clinic_hours.start_time} - {clinic_hours.end_time}")
            else:
                logger.warning("! No clinic hours found for Monday")

            # Test availability checking
            tomorrow = datetime.now() + timedelta(days=1)
            day_after = tomorrow + timedelta(days=1)

            available_slots = await appointment_service.check_availability(tomorrow, day_after)
            logger.info(f"✓ Found {len(available_slots)} available slots")

            if available_slots:
                logger.info(f"  First slot: {available_slots[0]['start']} - {available_slots[0]['end']}")

            # Test booking appointment
            patient_service = PatientService(session)
            test_input = BookAppointmentInput(
                name="Jane Smith",
                email="jane.smith@example.com",
                phone="555-0200",
                reason="Follow-up visit",
                slot_start="2025-11-14T14:00:00+00:00",
                slot_end="2025-11-14T14:30:00+00:00",
                insurance="Aetna"
            )

            patient = await patient_service.find_or_create_patient(test_input)

            start_time = datetime.fromisoformat(test_input.slot_start)
            end_time = datetime.fromisoformat(test_input.slot_end)

            appointment = await appointment_service.book_appointment(
                patient=patient,
                start_time=start_time,
                end_time=end_time,
                reason=test_input.reason
            )

            logger.info(f"✓ Booked appointment ID {appointment.id} for {patient.name}")

            # Test conflict detection
            try:
                await appointment_service.book_appointment(
                    patient=patient,
                    start_time=start_time,
                    end_time=end_time,
                    reason="Another appointment"
                )
                logger.error("✗ Conflict detection failed - should have raised ValueError")
            except ValueError as e:
                logger.info(f"✓ Conflict detection working: {e}")

            await session.commit()
            logger.info("✓ AppointmentService tests passed!")

        except Exception as e:
            await session.rollback()
            logger.error(f"✗ AppointmentService test failed: {e}")
            raise

async def main():
    """Run all service tests."""
    logger.info("Starting service layer tests...")

    try:
        await test_patient_service()
        await test_appointment_service()
        logger.info("\n✓ All service tests passed successfully!")
    except Exception as e:
        logger.error(f"\n✗ Service tests failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
