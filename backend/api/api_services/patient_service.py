"""
Extended Patient Service for FastAPI with full CRUD operations.
Imports and extends the existing PatientService from agent-python.
"""
import sys
from pathlib import Path

# Add agent-python to path
backend_dir = Path(__file__).parent.parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from models.patient import Patient
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PatientAPIService:
    """Extended patient service for REST API operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_patients(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> tuple[list[Patient], int]:
        """
        Get all patients with pagination and optional search.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Optional search term for name or email
            
        Returns:
            Tuple of (patients list, total count)
        """
        # Build base query
        query = select(Patient)
        count_query = select(func.count(Patient.id))

        # Add search filter if provided
        if search:
            search_filter = (
                Patient.name.ilike(f"%{search}%") |
                Patient.email.ilike(f"%{search}%") |
                Patient.phone.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.order_by(Patient.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        patients = result.scalars().all()

        logger.info(f"Retrieved {len(patients)} patients (total: {total})")
        return list(patients), total

    async def get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID."""
        stmt = select(Patient).where(Patient.id == patient_id)
        result = await self.session.execute(stmt)
        patient = result.scalar_one_or_none()
        
        if patient:
            logger.info(f"Found patient ID {patient_id}")
        else:
            logger.warning(f"Patient ID {patient_id} not found")
        
        return patient

    async def get_patient_by_email(self, email: str) -> Optional[Patient]:
        """Get patient by email address."""
        stmt = select(Patient).where(Patient.email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_patient(
        self,
        name: str,
        email: str,
        phone: str,
        insurance_provider: Optional[str] = None
    ) -> Patient:
        """
        Create a new patient.
        
        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing = await self.get_patient_by_email(email)
        if existing:
            raise ValueError(f"Patient with email {email} already exists")

        patient = Patient(
            name=name,
            email=email.lower(),
            phone=phone,
            insurance_provider=insurance_provider
        )
        self.session.add(patient)
        await self.session.flush()
        logger.info(f"Created patient ID {patient.id}: {email}")
        return patient

    async def update_patient(
        self,
        patient_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        insurance_provider: Optional[str] = None
    ) -> Patient:
        """
        Update patient information.
        
        Raises:
            ValueError: If patient not found or email already exists
        """
        patient = await self.get_patient_by_id(patient_id)
        if not patient:
            raise ValueError(f"Patient ID {patient_id} not found")

        # Check email uniqueness if changing email
        if email and email.lower() != patient.email:
            existing = await self.get_patient_by_email(email)
            if existing:
                raise ValueError(f"Email {email} already in use by another patient")
            patient.email = email.lower()

        # Update fields if provided
        if name:
            patient.name = name
        if phone:
            patient.phone = phone
        if insurance_provider is not None:  # Allow setting to None
            patient.insurance_provider = insurance_provider

        await self.session.flush()
        logger.info(f"Updated patient ID {patient_id}")
        return patient

    async def delete_patient(self, patient_id: int) -> bool:
        """
        Delete a patient.
        
        Note: This will cascade delete all appointments due to FK constraint.
        
        Returns:
            True if deleted, False if not found
        """
        patient = await self.get_patient_by_id(patient_id)
        if not patient:
            return False

        await self.session.delete(patient)
        await self.session.flush()
        logger.info(f"Deleted patient ID {patient_id}")
        return True
