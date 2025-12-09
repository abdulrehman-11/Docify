from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_,func
from sqlalchemy.orm import selectinload
from models.appointment import Appointment, AppointmentStatus
from models.clinic_hours import ClinicHours, ClinicHoliday
from models.patient import Patient
from datetime import datetime, timedelta, time, date as date_type
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

    async def get_holiday(self, check_date: date_type) -> ClinicHoliday | None:
        """Check if a specific date is a clinic holiday."""
        stmt = select(ClinicHoliday).where(ClinicHoliday.date == check_date)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_holidays(self) -> list[ClinicHoliday]:
        """Get all clinic holidays."""
        stmt = select(ClinicHoliday).order_by(ClinicHoliday.date)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_clinic_hours(self) -> list[ClinicHours]:
        """Get clinic hours for all days."""
        stmt = select(ClinicHours).order_by(ClinicHours.day_of_week)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def check_availability(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> list[dict[str, str]]:
        """
        Generate available 30-minute slots between start_date and end_date.
        Excludes already booked slots, slots outside clinic hours,
        break time slots, and holidays.

        Args:
            start_date: Start of time window (ISO8601)
            end_date: End of time window (ISO8601)

        Returns:
            List of available slots with start/end times
        """
        # ⚡ OPTIMIZATION: Batch all database queries upfront (3 queries instead of 21+)
        logger.info(f"🔍 Fetching availability data (batched queries)...")
        
        # Query 1: Get all clinic hours once (instead of per-day queries)
        all_clinic_hours = await self.get_all_clinic_hours()
        hours_by_day = {h.day_of_week: h for h in all_clinic_hours}
        
        # Query 2: Get all holidays once
        all_holidays = await self.get_all_holidays()
        holidays_by_date = {h.date: h for h in all_holidays}
        
        # Query 3: Get all booked slots for the entire date range once
        all_booked_slots = await self._get_booked_slots_range(
            start_date.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        
        logger.info(f"✅ Data fetched: {len(hours_by_day)} clinic hour configs, {len(holidays_by_date)} holidays, {len(all_booked_slots)} booked slots")
        
        # Now process in-memory (no more database queries)
        available_slots = []
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        while current_date <= end_date:
            # Check if this date is a holiday (from cached data)
            holiday = holidays_by_date.get(current_date.date())
            if holiday:
                if holiday.is_full_day:
                    # Full day holiday - skip entire day
                    logger.debug(f"Skipping {current_date.date()} - holiday: {holiday.name}")
                    current_date += timedelta(days=1)
                    continue
                else:
                    # Partial day holiday with custom hours
                    if holiday.start_time and holiday.end_time:
                        # Generate slots only for custom hours on holiday
                        day_slots = self._generate_slots_for_day_inmemory(
                            current_date,
                            holiday.start_time,
                            holiday.end_time,
                            break_start=None,
                            break_end=None,
                            booked_slots=all_booked_slots
                        )
                        available_slots.extend(day_slots)
                        current_date += timedelta(days=1)
                        continue

            day_of_week = current_date.weekday()  # 0=Monday
            clinic_hours = hours_by_day.get(day_of_week)

            if not clinic_hours or not clinic_hours.is_active:
                # Clinic closed on this day
                current_date += timedelta(days=1)
                continue

            # Generate slots for this day, excluding break time (using cached booked slots)
            day_slots = self._generate_slots_for_day_inmemory(
                current_date,
                clinic_hours.start_time,
                clinic_hours.end_time,
                break_start=clinic_hours.break_start,
                break_end=clinic_hours.break_end,
                booked_slots=all_booked_slots
            )
            available_slots.extend(day_slots)
            current_date += timedelta(days=1)

        # Filter by requested time window
        filtered_slots = [
            slot for slot in available_slots
            if start_date <= datetime.fromisoformat(slot["start"]) <= end_date
        ]

        logger.info(f"✅ Found {len(filtered_slots)} available slots between {start_date.date()} and {end_date.date()}")
        return filtered_slots

    async def _generate_slots_for_day(
        self,
        date: datetime,
        clinic_start: time,
        clinic_end: time,
        break_start: time | None = None,
        break_end: time | None = None
    ) -> list[dict[str, str]]:
        """Generate all possible 30-min slots for a single day, excluding break time."""
        slots = []
        current_time = datetime.combine(date.date(), clinic_start)
        end_time = datetime.combine(date.date(), clinic_end)

        # Create break time datetime objects if break times exist
        break_start_dt = None
        break_end_dt = None
        if break_start and break_end:
            break_start_dt = datetime.combine(date.date(), break_start)
            break_end_dt = datetime.combine(date.date(), break_end)
            if date.tzinfo is not None:
                break_start_dt = break_start_dt.replace(tzinfo=date.tzinfo)
                break_end_dt = break_end_dt.replace(tzinfo=date.tzinfo)

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

            # Check if slot overlaps with break time
            is_during_break = False
            if break_start_dt and break_end_dt:
                # A slot is during break if it overlaps with break period
                is_during_break = self._slots_overlap(slot_start, slot_end, break_start_dt, break_end_dt)

            # Check if slot overlaps with any booked appointment
            is_booked = any(
                self._slots_overlap(slot_start, slot_end, booked_start, booked_end)
                for booked_start, booked_end in booked_slots
            )

            if not is_during_break and not is_booked:
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

    async def _get_booked_slots_range(self, start_date: datetime, end_date: datetime) -> list[tuple[datetime, datetime]]:
        """⚡ OPTIMIZED: Get all booked appointment slots for entire date range in ONE query."""
        stmt = select(Appointment.start_time, Appointment.end_time).where(
            and_(
                Appointment.start_time >= start_date,
                Appointment.start_time <= end_date,
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

    def _generate_slots_for_day_inmemory(
        self,
        date: datetime,
        clinic_start: time,
        clinic_end: time,
        break_start: time | None = None,
        break_end: time | None = None,
        booked_slots: list[tuple[datetime, datetime]] = None
    ) -> list[dict[str, str]]:
        """⚡ OPTIMIZED: Generate slots using pre-fetched booked_slots (no database query)."""
        slots = []
        current_time = datetime.combine(date.date(), clinic_start)
        end_time = datetime.combine(date.date(), clinic_end)

        # Create break time datetime objects if break times exist
        break_start_dt = None
        break_end_dt = None
        if break_start and break_end:
            break_start_dt = datetime.combine(date.date(), break_start)
            break_end_dt = datetime.combine(date.date(), break_end)
            if date.tzinfo is not None:
                break_start_dt = break_start_dt.replace(tzinfo=date.tzinfo)
                break_end_dt = break_end_dt.replace(tzinfo=date.tzinfo)

        # Preserve timezone info if date has it
        if date.tzinfo is not None:
            current_time = current_time.replace(tzinfo=date.tzinfo)
            end_time = end_time.replace(tzinfo=date.tzinfo)

        # Don't allow booking slots in the past
        now = datetime.now(current_time.tzinfo) if current_time.tzinfo else datetime.now()
        if current_time < now:
            current_time = now

        # Use pre-fetched booked slots (already in memory)
        if booked_slots is None:
            booked_slots = []

        while current_time + timedelta(minutes=self.SLOT_DURATION_MINUTES) <= end_time:
            slot_start = current_time
            slot_end = current_time + timedelta(minutes=self.SLOT_DURATION_MINUTES)

            # Check if slot overlaps with break time
            is_during_break = False
            if break_start_dt and break_end_dt:
                is_during_break = self._slots_overlap(slot_start, slot_end, break_start_dt, break_end_dt)

            # Check if slot overlaps with any booked appointment (from pre-fetched list)
            is_booked = any(
                self._slots_overlap(slot_start, slot_end, booked_start, booked_end)
                for booked_start, booked_end in booked_slots
            )

            if not is_during_break and not is_booked:
                slots.append({
                    "start": slot_start.isoformat(),
                    "end": slot_end.isoformat()
                })

            current_time = slot_end

        return slots

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
       
        stmt = (
            select(Appointment)
            .options(selectinload(Appointment.patient))
            .where(Appointment.id == appointment_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        old_appointment = result.scalar_one_or_none()

        if not old_appointment:
            raise ValueError(f"Appointment {appointment_id} not found")

        # Store info about cancelled status
        was_cancelled = old_appointment.status == AppointmentStatus.CANCELLED
        if was_cancelled:
            logger.info(f"Rescheduling cancelled appointment {appointment_id} - will reactivate")

        # Check new slot availability (exclude the old appointment and only check confirmed ones)
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

        # Mark old as rescheduled (even if it was cancelled)
        old_appointment.status = AppointmentStatus.RESCHEDULED

        # Get patient (already loaded via selectinload above)
        patient = old_appointment.patient

        # Create new appointment (always with CONFIRMED status - this reactivates cancelled ones)
        new_appointment = Appointment(
            patient_id=old_appointment.patient_id,
            start_time=new_start_time,
            end_time=new_end_time,
            reason=old_appointment.reason,
            status=AppointmentStatus.CONFIRMED  # Always confirmed, even if old was cancelled
        )
        self.session.add(new_appointment)
        await self.session.flush()
        
        # Handle Google Calendar
        if CALENDAR_AVAILABLE and patient:
            try:
                calendar_service = get_calendar_service()
                
                # Delete old event if it exists (may not exist for cancelled appointments)
                if old_calendar_event_id:
                    deleted = calendar_service.delete_event(old_calendar_event_id)
                    if deleted:
                        logger.info(f"Deleted old calendar event {old_calendar_event_id}")
                    else:
                        logger.warning(f"Could not delete old calendar event {old_calendar_event_id}")
                
                # Always create new calendar event for rescheduled appointment
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
                    logger.info(f"Created calendar event {event_id} for {'reactivated' if was_cancelled else 'rescheduled'} appointment {new_appointment.id}")
            except Exception as e:
                logger.error(f"Failed to update calendar for reschedule: {e}")
        
        action = "Reactivated and rescheduled" if was_cancelled else "Rescheduled"
        logger.info(f"{action} appointment {appointment_id} to new appointment {new_appointment.id}")
        return new_appointment

    async def find_appointment(
        self,
        patient_name: str,
        start_time: datetime,
        include_cancelled: bool = False
    ) -> Appointment | None:
        """
        Find appointment by patient name and start time.
        
        Args:
            patient_name: Name of the patient
            start_time: Start time of the appointment
            include_cancelled: If True, includes cancelled and rescheduled appointments in search
        
        Returns:
            Appointment if found, None otherwise
        """
        conditions = [
            Patient.name == patient_name,
            Appointment.start_time == start_time,
        ]
        
        if not include_cancelled:
            conditions.append(Appointment.status == AppointmentStatus.CONFIRMED)
        
        stmt = (
            select(Appointment)
            .options(selectinload(Appointment.patient))
            .join(Patient)
            .where(and_(*conditions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_appointments_for_patient(
        self,
        patient_name: str,
        from_time: datetime | None = None,
        include_cancelled: bool = False
    ) -> list[Appointment]:
        """
        Get appointments for patient, optionally including cancelled ones.
        
        Args:
            patient_name: Name of the patient
            from_time: Only return appointments starting from this time (optional)
            include_cancelled: If True, includes cancelled and rescheduled appointments
        
        Returns:
            List of appointments sorted by start time
        """
        if from_time is None:
            from_time = datetime.utcnow()
        
        conditions = [
            func.lower(Patient.name) == patient_name.strip().lower(),
            Appointment.start_time >= from_time,
        ]
        
        if not include_cancelled:
            conditions.append(Appointment.status == AppointmentStatus.CONFIRMED)
        
        stmt = (
            select(Appointment)
            .options(selectinload(Appointment.patient))
            .join(Patient)
            .where(and_(*conditions))
            .order_by(Appointment.start_time.asc())
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_upcoming_appointments_for_patient(
        self,
        patient_name: str,
        from_time: datetime | None = None,
    ) -> list[Appointment]:
        """Return all future confirmed appointments for a patient from from_time onwards."""
        if from_time is None:
            # Use UTC "now" so comparison with stored timestamps is consistent
            from_time = datetime.utcnow()

        stmt = (
            select(Appointment)
            .join(Patient)
            .where(
                and_(
                    # Case-insensitive, trimmed name match to handle spelling/capitalization
                    func.lower(Patient.name) == patient_name.strip().lower(),
                    Appointment.start_time >= from_time,
                    Appointment.status == AppointmentStatus.CONFIRMED,
                )
            )
            .order_by(Appointment.start_time.asc())
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()