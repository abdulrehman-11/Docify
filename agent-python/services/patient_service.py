from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.patient import Patient
from tools.schemas import BookAppointmentInput
import logging

logger = logging.getLogger(__name__)

class PatientService:
    """Service for patient management with find-or-create pattern."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_or_create_patient(self, input_data: BookAppointmentInput) -> Patient:
        """
        Find existing patient by email or create new one.
        Implements deduplication to prevent duplicate patient records.

        Args:
            input_data: Booking input with patient details

        Returns:
            Patient: Existing or newly created patient
        """
        # Try to find existing patient by email
        stmt = select(Patient).where(Patient.email == input_data.email.lower())
        result = await self.session.execute(stmt)
        patient = result.scalar_one_or_none()

        if patient:
            logger.info(f"Found existing patient: {patient.email}")
            # Update patient info if changed
            patient.name = input_data.name
            patient.phone = input_data.phone
            if input_data.insurance:
                patient.insurance_provider = input_data.insurance
            await self.session.flush()
            return patient

        # Create new patient
        patient = Patient(
            name=input_data.name,
            email=input_data.email.lower(),
            phone=input_data.phone,
            insurance_provider=input_data.insurance if input_data.insurance else None
        )
        self.session.add(patient)
        await self.session.flush()  # Get patient.id before commit
        logger.info(f"Created new patient: {patient.email} (ID: {patient.id})")
        return patient

    async def get_patient_by_email(self, email: str) -> Patient | None:
        """Get patient by email address."""
        stmt = select(Patient).where(Patient.email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
