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
        Uses fuzzy matching as fallback for voice transcription errors.

        Args:
            input_data: Booking input with patient details

        Returns:
            Patient: Existing or newly created patient
        """
        # Try exact email match first
        stmt = select(Patient).where(Patient.email == input_data.email.lower())
        result = await self.session.execute(stmt)
        patient = result.scalar_one_or_none()

        # Try fuzzy email match if exact fails (handles voice transcription errors)
        if not patient:
            patient = await self.find_patient_by_email_fuzzy(input_data.email)

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

    async def find_patient_by_email_fuzzy(self, email: str, threshold: float = 0.85) -> Patient | None:
        """
        Find patient with fuzzy email matching for voice transcription errors.

        Uses Levenshtein distance to find similar emails when exact match fails.
        This helps prevent duplicate patient creation due to voice transcription errors.

        Args:
            email: Email address to search for
            threshold: Minimum similarity score (0-1) to consider a match (default 0.85 = 85%)

        Returns:
            Patient if fuzzy match found, None otherwise
        """
        from difflib import SequenceMatcher

        # Try exact match first
        exact_patient = await self.get_patient_by_email(email)
        if exact_patient:
            return exact_patient

        # Fuzzy match if exact fails
        stmt = select(Patient)
        result = await self.session.execute(stmt)
        all_patients = result.scalars().all()

        best_match = None
        best_score = 0

        for patient in all_patients:
            score = SequenceMatcher(None, email.lower(), patient.email.lower()).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = patient

        if best_match:
            logger.warning(
                f"⚠️  FUZZY EMAIL MATCH FOUND:\n"
                f"   Requested: '{email}'\n"
                f"   Matched:   '{best_match.email}'\n"
                f"   Similarity: {best_score:.1%}\n"
                f"   Patient ID: {best_match.id}\n"
                f"   ACTION: Using existing patient (avoiding duplicate creation)"
            )

        return best_match

    async def get_patient_by_phone(self, phone: str) -> Patient | None:
        """Get patient by phone number."""
        stmt = select(Patient).where(Patient.phone == phone)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
