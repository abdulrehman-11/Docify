"""
Extended Appointment Service for FastAPI with full CRUD operations.
Imports and extends the existing AppointmentService from agent-python.
Includes Google Calendar integration.
"""
import sys
from pathlib import Path

# Add agent-python to path
backend_dir = Path(__file__).parent.parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from models.appointment import Appointment, AppointmentStatus
from models.patient import Patient
from datetime import datetime, date, time, timedelta
from typing import Optional
import logging

# Import Google Calendar service
try:
    from services.google_calendar_service import get_calendar_service
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    get_calendar_service = None

logger = logging.getLogger(__name__)


class AppointmentAPIService:
    """Extended appointment service for REST API operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_appointments(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        patient_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[list[dict], int]:
        """
        Get all appointments with filters and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by appointment status
            patient_id: Filter by patient ID
            start_date: Filter appointments after this date
            end_date: Filter appointments before this date
            
        Returns:
            Tuple of (appointments with patient data, total count)
        """
        # Build base query with patient join
        query = select(Appointment, Patient).join(
            Patient, Appointment.patient_id == Patient.id
        )
        count_query = select(func.count(Appointment.id))

        # Build filters
        filters = []
        if status:
            filters.append(Appointment.status == AppointmentStatus[status])
        if patient_id:
            filters.append(Appointment.patient_id == patient_id)
        if start_date:
            filters.append(Appointment.start_time >= start_date)
        if end_date:
            filters.append(Appointment.start_time <= end_date)

        # Apply filters
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.order_by(Appointment.start_time.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        rows = result.all()

        # Format response with patient data
        appointments = []
        for appointment, patient in rows:
            appointments.append({
                "id": appointment.id,
                "patient_id": appointment.patient_id,
                "patient_name": patient.name,
                "patient_email": patient.email,
                "patient_phone": patient.phone,
                "start_time": appointment.start_time,
                "end_time": appointment.end_time,
                "reason": appointment.reason,
                "status": appointment.status.value,
                "cancellation_reason": appointment.cancellation_reason,
                "created_at": appointment.created_at,
                "updated_at": appointment.updated_at,
            })

        logger.info(f"Retrieved {len(appointments)} appointments (total: {total})")
        return appointments, total

    async def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment by ID."""
        stmt = select(Appointment).where(Appointment.id == appointment_id)
        result = await self.session.execute(stmt)
        appointment = result.scalar_one_or_none()
        
        if appointment:
            logger.info(f"Found appointment ID {appointment_id}")
        else:
            logger.warning(f"Appointment ID {appointment_id} not found")
        
        return appointment

    async def create_appointment(
        self,
        patient_id: int,
        start_time: datetime,
        end_time: datetime,
        reason: str
    ) -> Appointment:
        """
        Create a new appointment with Google Calendar integration.
        
        Raises:
            ValueError: If patient not found or slot not available
        """
        # Verify patient exists
        patient_stmt = select(Patient).where(Patient.id == patient_id)
        patient_result = await self.session.execute(patient_stmt)
        patient = patient_result.scalar_one_or_none()
        
        if not patient:
            raise ValueError(f"Patient ID {patient_id} not found")

        # Check for conflicts
        conflict_stmt = select(Appointment).where(
            and_(
                Appointment.start_time < end_time,
                Appointment.end_time > start_time,
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        )
        conflict_result = await self.session.execute(conflict_stmt)
        conflicting = conflict_result.scalars().all()

        if conflicting:
            raise ValueError("Time slot is not available - conflicts with existing appointment")

        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            status=AppointmentStatus.CONFIRMED
        )
        self.session.add(appointment)
        await self.session.flush()
        
        # Create Google Calendar event
        if CALENDAR_AVAILABLE:
            try:
                calendar_service = get_calendar_service()
                event_id = calendar_service.create_event(
                    patient_name=patient.name,
                    patient_email=patient.email,
                    patient_phone=patient.phone,
                    reason=reason,
                    start_time=start_time,
                    end_time=end_time,
                    appointment_id=appointment.id
                )
                if event_id:
                    appointment.google_calendar_event_id = event_id
                    await self.session.flush()
                    logger.info(f"Created calendar event {event_id} for appointment {appointment.id}")
            except Exception as e:
                logger.error(f"Failed to create calendar event: {e}")
                # Continue without calendar - appointment is still valid
        
        logger.info(f"Created appointment ID {appointment.id}")
        return appointment

    async def update_appointment(
        self,
        appointment_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        reason: Optional[str] = None,
        status: Optional[str] = None,
        cancellation_reason: Optional[str] = None
    ) -> Appointment:
        """
        Update appointment with Google Calendar sync.
        
        Raises:
            ValueError: If appointment not found or time conflict
        """
        appointment = await self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise ValueError(f"Appointment ID {appointment_id} not found")

        # If changing time, check for conflicts
        new_start = start_time if start_time else appointment.start_time
        new_end = end_time if end_time else appointment.end_time
        time_changed = start_time or end_time

        if time_changed:
            conflict_stmt = select(Appointment).where(
                and_(
                    Appointment.id != appointment_id,
                    Appointment.start_time < new_end,
                    Appointment.end_time > new_start,
                    Appointment.status == AppointmentStatus.CONFIRMED
                )
            )
            conflict_result = await self.session.execute(conflict_stmt)
            conflicting = conflict_result.scalars().all()

            if conflicting:
                raise ValueError("New time slot conflicts with existing appointment")

            appointment.start_time = new_start
            appointment.end_time = new_end

        # Update other fields
        if reason:
            appointment.reason = reason
        if status:
            appointment.status = AppointmentStatus[status]
        if cancellation_reason is not None:
            appointment.cancellation_reason = cancellation_reason

        await self.session.flush()
        
        # Update Google Calendar event if time changed
        if time_changed and appointment.google_calendar_event_id and CALENDAR_AVAILABLE:
            try:
                # Get patient info
                patient_stmt = select(Patient).where(Patient.id == appointment.patient_id)
                patient_result = await self.session.execute(patient_stmt)
                patient = patient_result.scalar_one_or_none()
                
                if patient:
                    calendar_service = get_calendar_service()
                    calendar_service.update_event(
                        event_id=appointment.google_calendar_event_id,
                        patient_name=patient.name,
                        patient_email=patient.email,
                        patient_phone=patient.phone,
                        reason=appointment.reason,
                        start_time=new_start,
                        end_time=new_end,
                        appointment_id=appointment_id
                    )
                    logger.info(f"Updated calendar event for appointment {appointment_id}")
            except Exception as e:
                logger.error(f"Failed to update calendar event: {e}")
        
        logger.info(f"Updated appointment ID {appointment_id}")
        return appointment

    async def cancel_appointment(
        self,
        appointment_id: int,
        cancellation_reason: Optional[str] = None
    ) -> Appointment:
        """Cancel an appointment and delete from Google Calendar."""
        appointment = await self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise ValueError(f"Appointment ID {appointment_id} not found")

        if appointment.status == AppointmentStatus.CANCELLED:
            raise ValueError("Appointment is already cancelled")

        # Store calendar event ID before cancelling
        calendar_event_id = appointment.google_calendar_event_id

        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = cancellation_reason
        await self.session.flush()
        
        # Delete from Google Calendar
        if calendar_event_id and CALENDAR_AVAILABLE:
            try:
                calendar_service = get_calendar_service()
                calendar_service.delete_event(calendar_event_id)
                logger.info(f"Deleted calendar event {calendar_event_id}")
            except Exception as e:
                logger.error(f"Failed to delete calendar event: {e}")
        
        logger.info(f"Cancelled appointment ID {appointment_id}")
        return appointment

    async def delete_appointment(self, appointment_id: int) -> bool:
        """
        Delete an appointment (hard delete) and remove from Google Calendar.
        
        Returns:
            True if deleted, False if not found
        """
        appointment = await self.get_appointment_by_id(appointment_id)
        if not appointment:
            return False

        # Store calendar event ID before deleting
        calendar_event_id = appointment.google_calendar_event_id

        await self.session.delete(appointment)
        await self.session.flush()
        
        # Delete from Google Calendar
        if calendar_event_id and CALENDAR_AVAILABLE:
            try:
                calendar_service = get_calendar_service()
                calendar_service.delete_event(calendar_event_id)
                logger.info(f"Deleted calendar event {calendar_event_id}")
            except Exception as e:
                logger.error(f"Failed to delete calendar event: {e}")
        
        logger.info(f"Deleted appointment ID {appointment_id}")
        return True

    async def get_today_appointments(self) -> list[dict]:
        """Get all appointments for today."""
        today = datetime.now().date()
        start_of_day = datetime.combine(today, time.min)
        end_of_day = datetime.combine(today, time.max)

        query = select(Appointment, Patient).join(
            Patient, Appointment.patient_id == Patient.id
        ).where(
            and_(
                Appointment.start_time >= start_of_day,
                Appointment.start_time <= end_of_day,
                Appointment.status != AppointmentStatus.CANCELLED
            )
        ).order_by(Appointment.start_time)

        result = await self.session.execute(query)
        rows = result.all()

        appointments = []
        for appointment, patient in rows:
            appointments.append({
                "id": appointment.id,
                "patient_name": patient.name,
                "patient_phone": patient.phone,
                "start_time": appointment.start_time,
                "end_time": appointment.end_time,
                "reason": appointment.reason,
                "status": appointment.status.value,
            })

        logger.info(f"Found {len(appointments)} appointments for today")
        return appointments

    async def get_upcoming_appointments(self, days: int = 7) -> list[dict]:
        """Get upcoming appointments for next N days."""
        now = datetime.now()
        future = now + timedelta(days=days)

        query = select(Appointment, Patient).join(
            Patient, Appointment.patient_id == Patient.id
        ).where(
            and_(
                Appointment.start_time >= now,
                Appointment.start_time <= future,
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        ).order_by(Appointment.start_time)

        result = await self.session.execute(query)
        rows = result.all()

        appointments = []
        for appointment, patient in rows:
            appointments.append({
                "id": appointment.id,
                "patient_name": patient.name,
                "patient_email": patient.email,
                "patient_phone": patient.phone,
                "start_time": appointment.start_time,
                "end_time": appointment.end_time,
                "reason": appointment.reason,
                "status": appointment.status.value,
            })

        logger.info(f"Found {len(appointments)} upcoming appointments")
        return appointments

    async def get_appointment_stats(self) -> dict:
        """Get appointment statistics for dashboard."""
        today = datetime.now().date()
        start_of_day = datetime.combine(today, time.min)
        end_of_day = datetime.combine(today, time.max)
        now = datetime.now()

        # Today's appointments
        today_count_stmt = select(func.count(Appointment.id)).where(
            and_(
                Appointment.start_time >= start_of_day,
                Appointment.start_time <= end_of_day
            )
        )
        today_result = await self.session.execute(today_count_stmt)
        today_count = today_result.scalar()

        # Upcoming appointments
        upcoming_count_stmt = select(func.count(Appointment.id)).where(
            and_(
                Appointment.start_time >= now,
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        )
        upcoming_result = await self.session.execute(upcoming_count_stmt)
        upcoming_count = upcoming_result.scalar()

        # Total patients
        patient_count_stmt = select(func.count(Patient.id))
        patient_result = await self.session.execute(patient_count_stmt)
        patient_count = patient_result.scalar()

        # Confirmed appointments
        confirmed_stmt = select(func.count(Appointment.id)).where(
            Appointment.status == AppointmentStatus.CONFIRMED
        )
        confirmed_result = await self.session.execute(confirmed_stmt)
        confirmed_count = confirmed_result.scalar()

        # Cancelled appointments
        cancelled_stmt = select(func.count(Appointment.id)).where(
            Appointment.status == AppointmentStatus.CANCELLED
        )
        cancelled_result = await self.session.execute(cancelled_stmt)
        cancelled_count = cancelled_result.scalar()

        # Completed appointments
        completed_stmt = select(func.count(Appointment.id)).where(
            Appointment.status == AppointmentStatus.COMPLETED
        )
        completed_result = await self.session.execute(completed_stmt)
        completed_count = completed_result.scalar()

        stats = {
            "total_appointments_today": today_count,
            "total_appointments_upcoming": upcoming_count,
            "total_patients": patient_count,
            "confirmed_appointments": confirmed_count,
            "cancelled_appointments": cancelled_count,
            "completed_appointments": completed_count,
        }

        logger.info(f"Generated dashboard stats: {stats}")
        return stats
