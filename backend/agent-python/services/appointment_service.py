from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.appointment import Appointment, AppointmentStatus
from models.clinic_hours import ClinicHours
from models.patient import Patient
from datetime import datetime, timedelta, time
import logging

# Import Google Calendar service
try:
    from services.google_calendar_service import get_calendar_service
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    get_calendar_service = None

logger = logging.getLogger(__name__)

class AppointmentService:
    """Service for appointment management with conflict detection."""

    SLOT_DURATION_MINUTES = 30

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_clinic_hours(self, day_of_week: int) -> ClinicHours | None:
        """Get clinic hours for specific day (0=Monday, 6=Sunday)."""
        stmt = select(ClinicHours).where(
            and_(
                ClinicHours.day_of_week == day_of_week,
                ClinicHours.is_active == True
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def check_availability(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> list[dict[str, str]]:
        """
        Generate available 30-minute slots between start_date and end_date.
        Excludes already booked slots and slots outside clinic hours.

        Args:
            start_date: Start of time window (ISO8601)
            end_date: End of time window (ISO8601)

        Returns:
            List of available slots with start/end times
        """
        available_slots = []
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        while current_date <= end_date:
            day_of_week = current_date.weekday()  # 0=Monday
            clinic_hours = await self.get_clinic_hours(day_of_week)

            if not clinic_hours:
                # Clinic closed on this day
                current_date += timedelta(days=1)
                continue

            # Generate slots for this day
            day_slots = await self._generate_slots_for_day(
                current_date,
                clinic_hours.start_time,
                clinic_hours.end_time
            )
            available_slots.extend(day_slots)
            current_date += timedelta(days=1)

        # Filter by requested time window
        filtered_slots = [
            slot for slot in available_slots
            if start_date <= datetime.fromisoformat(slot["start"]) <= end_date
        ]

        logger.info(f"Found {len(filtered_slots)} available slots between {start_date} and {end_date}")
        return filtered_slots

    async def _generate_slots_for_day(
        self,
        date: datetime,
        clinic_start: time,
        clinic_end: time
    ) -> list[dict[str, str]]:
        """Generate all possible 30-min slots for a single day."""
        slots = []
        current_time = datetime.combine(date.date(), clinic_start)
        end_time = datetime.combine(date.date(), clinic_end)

        # Preserve timezone info if date has it
        if date.tzinfo is not None:
            current_time = current_time.replace(tzinfo=date.tzinfo)
            end_time = end_time.replace(tzinfo=date.tzinfo)

        # Don't allow booking slots in the past
        now = datetime.now(current_time.tzinfo) if current_time.tzinfo else datetime.now()
        if current_time < now:
            current_time = now

        # Get all booked appointments for this day
        booked_slots = await self._get_booked_slots(date)

        while current_time + timedelta(minutes=self.SLOT_DURATION_MINUTES) <= end_time:
            slot_start = current_time
            slot_end = current_time + timedelta(minutes=self.SLOT_DURATION_MINUTES)

            # Check if slot overlaps with any booked appointment
            is_available = not any(
                self._slots_overlap(slot_start, slot_end, booked_start, booked_end)
                for booked_start, booked_end in booked_slots
            )

            if is_available:
                slots.append({
                    "start": slot_start.isoformat(),
                    "end": slot_end.isoformat()
                })

            current_time = slot_end

        return slots

    async def _get_booked_slots(self, date: datetime) -> list[tuple[datetime, datetime]]:
        """Get all booked appointment slots for a specific day."""
        day_start = datetime.combine(date.date(), time.min).replace(tzinfo=date.tzinfo)
        day_end = datetime.combine(date.date(), time.max).replace(tzinfo=date.tzinfo)

        stmt = select(Appointment.start_time, Appointment.end_time).where(
            and_(
                Appointment.start_time >= day_start,
                Appointment.start_time < day_end,
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        )
        result = await self.session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    def _slots_overlap(
        self,
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """Check if two time slots overlap."""
        return start1 < end2 and end1 > start2

    async def book_appointment(
        self,
        patient: Patient,
        start_time: datetime,
        end_time: datetime,
        reason: str
    ) -> Appointment:
        """
        Book appointment with SELECT FOR UPDATE locking to prevent double-booking.

        Args:
            patient: Patient object
            start_time: Appointment start (ISO8601)
            end_time: Appointment end (ISO8601)
            reason: Reason for visit

        Returns:
            Appointment: Created appointment

        Raises:
            ValueError: If slot is not available (conflict detected)
        """
        # Lock all overlapping appointments to prevent race conditions
        stmt = select(Appointment).where(
            and_(
                Appointment.start_time < end_time,
                Appointment.end_time > start_time,
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        ).with_for_update()

        result = await self.session.execute(stmt)
        conflicting = result.scalars().all()

        if conflicting:
            logger.warning(f"Booking conflict detected for slot {start_time} - {end_time}")
            raise ValueError("Time slot is no longer available. Please choose another time.")

        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            status=AppointmentStatus.CONFIRMED
        )
        self.session.add(appointment)
        await self.session.flush()  # Get appointment.id
        
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
        
        logger.info(f"Booked appointment ID {appointment.id} for patient {patient.email}")
        return appointment

    async def cancel_appointment(
        self,
        appointment_id: int,
        cancellation_reason: str | None = None
    ) -> Appointment:
        """Cancel appointment by ID."""
        stmt = select(Appointment).where(Appointment.id == appointment_id).with_for_update()
        result = await self.session.execute(stmt)
        appointment = result.scalar_one_or_none()

        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")

        if appointment.status == AppointmentStatus.CANCELLED:
            raise ValueError(f"Appointment {appointment_id} is already cancelled")

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

    async def reschedule_appointment(
        self,
        appointment_id: int,
        new_start_time: datetime,
        new_end_time: datetime
    ) -> Appointment:
        """
        Reschedule appointment atomically (cancel old + book new).
        Uses transaction to ensure consistency.
        """
        # Get and lock old appointment
        stmt = select(Appointment).where(Appointment.id == appointment_id).with_for_update()
        result = await self.session.execute(stmt)
        old_appointment = result.scalar_one_or_none()

        if not old_appointment:
            raise ValueError(f"Appointment {appointment_id} not found")

        # Check new slot availability
        stmt = select(Appointment).where(
            and_(
                Appointment.id != appointment_id,  # Exclude current appointment
                Appointment.start_time < new_end_time,
                Appointment.end_time > new_start_time,
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        ).with_for_update()

        result = await self.session.execute(stmt)
        conflicting = result.scalars().all()

        if conflicting:
            raise ValueError("New time slot is not available")

        # Store old calendar event ID
        old_calendar_event_id = old_appointment.google_calendar_event_id

        # Mark old as rescheduled
        old_appointment.status = AppointmentStatus.RESCHEDULED

        # Get patient for calendar event
        patient_stmt = select(Patient).where(Patient.id == old_appointment.patient_id)
        patient_result = await self.session.execute(patient_stmt)
        patient = patient_result.scalar_one_or_none()

        # Create new appointment
        new_appointment = Appointment(
            patient_id=old_appointment.patient_id,
            start_time=new_start_time,
            end_time=new_end_time,
            reason=old_appointment.reason,
            status=AppointmentStatus.CONFIRMED
        )
        self.session.add(new_appointment)
        await self.session.flush()
        
        # Handle Google Calendar - delete old event and create new one
        if CALENDAR_AVAILABLE and patient:
            try:
                calendar_service = get_calendar_service()
                
                # Delete old event if exists
                if old_calendar_event_id:
                    calendar_service.delete_event(old_calendar_event_id)
                    logger.info(f"Deleted old calendar event {old_calendar_event_id}")
                
                # Create new calendar event
                event_id = calendar_service.create_event(
                    patient_name=patient.name,
                    patient_email=patient.email,
                    patient_phone=patient.phone,
                    reason=old_appointment.reason,
                    start_time=new_start_time,
                    end_time=new_end_time,
                    appointment_id=new_appointment.id
                )
                if event_id:
                    new_appointment.google_calendar_event_id = event_id
                    await self.session.flush()
                    logger.info(f"Created calendar event {event_id} for rescheduled appointment {new_appointment.id}")
            except Exception as e:
                logger.error(f"Failed to update calendar for reschedule: {e}")
        
        logger.info(f"Rescheduled appointment {appointment_id} to new appointment {new_appointment.id}")
        return new_appointment

    async def find_appointment(
        self,
        patient_name: str,
        start_time: datetime
    ) -> Appointment | None:
        """Find appointment by patient name and start time."""
        stmt = select(Appointment).join(Patient).where(
            and_(
                Patient.name == patient_name,
                Appointment.start_time == start_time,
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
