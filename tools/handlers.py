import logging
from .schemas import (
  CheckAvailabilityInput, CheckAvailabilityOutput,
  Slot,
  BookAppointmentInput, BookAppointmentOutput,
  CancelAppointmentInput, CancelAppointmentOutput,
  RescheduleAppointmentInput, RescheduleAppointmentOutput,
  GetUpcomingAppointmentsInput, GetUpcomingAppointmentsOutput,
  GetHoursInput, GetHoursOutput,
  GetLocationInput, GetLocationOutput,
  GetInsuranceSupportedInput, GetInsuranceSupportedOutput,
  EscalateToHumanInput, EscalateToHumanOutput,
  SendConfirmationInput, SendConfirmationOutput,
  LookupAppointmentInput, LookupAppointmentOutput, AppointmentInfo,
)
from .router import ToolRouter
from datetime import datetime, timedelta
from services.appointment_service import AppointmentService
from services.patient_service import PatientService
from services.google_calendar_service import get_calendar_service
from services.email_service import get_email_service  # ADD THIS IMPORT
from utils.sanitize import sanitize_name, sanitize_email

logger = logging.getLogger(__name__)

# Session factory will be passed from agent.py
_session_factory = None

def set_session_factory(factory):
    """Set the database session factory."""
    global _session_factory
    _session_factory = factory


async def check_availability(i: CheckAvailabilityInput) -> CheckAvailabilityOutput:
  """Check available appointment slots within time window."""
  logger.info("="*60)
  logger.info("🔍 EXECUTING check_availability handler")
  logger.info(f"📅 Reason: {i.reason}")
  
  async with _session_factory() as session:
    service = AppointmentService(session)

    # Parse preferred time window
    start_time = datetime.fromisoformat(i.preferred_time_window.from_.replace("Z", "+00:00"))
    end_time = datetime.fromisoformat(i.preferred_time_window.to.replace("Z", "+00:00"))
    
    logger.info(f"⏰ Checking from: {start_time.strftime('%Y-%m-%d %H:%M')}")
    logger.info(f"⏰ Checking to:   {end_time.strftime('%Y-%m-%d %H:%M')}")

    # TIME THIS OPERATION
    import time as time_module
    start = time_module.time()
    
    slots = await service.check_availability(start_time, end_time)
    
    elapsed = time_module.time() - start
    logger.info(f"⚡ Database query took: {elapsed*1000:.0f}ms")
    logger.info(f"✅ Found {len(slots)} available slots")

    # Debug logging: Show slot times in readable format
    if slots:
      slot_times = [slot["start"][11:16] for slot in slots[:5]]
      logger.info(f"📋 Sample slots (HH:MM): {', '.join(slot_times)}")
    else:
      logger.warning("⚠️  NO SLOTS FOUND - Day might be fully booked or outside clinic hours")
    
    logger.info("="*60)

    return CheckAvailabilityOutput(slots=[
      Slot(start=slot["start"], end=slot["end"]) for slot in slots
    ])

async def book_appointment(i: BookAppointmentInput) -> BookAppointmentOutput:
  """Book appointment with conflict detection, Google Calendar, and EMAIL confirmation."""
  safe_name = sanitize_name(i.name)
  safe_email = sanitize_email(i.email)

  logger.info("Executing book_appointment handler")
  logger.info(f"Booking details - Name: {safe_name}, Email: {safe_email}, Slot: {i.slot_start[11:16]}-{i.slot_end[11:16]}")

  async with _session_factory() as session:
    try:
      # Find or create patient
      patient_service = PatientService(session)
      # Pass sanitized name/email into patient creation
      i.name = safe_name
      i.email = safe_email
      patient = await patient_service.find_or_create_patient(i)
      logger.info(f"Patient resolved - ID: {patient.id}, Email: {patient.email}")

      # Book appointment with locking
      appointment_service = AppointmentService(session)
      start_time = datetime.fromisoformat(i.slot_start.replace("Z", "+00:00"))
      end_time = datetime.fromisoformat(i.slot_end.replace("Z", "+00:00"))
      appointment = await appointment_service.book_appointment(
        patient=patient,
        start_time=start_time,
        end_time=end_time,
        reason=i.reason
      )

      # Commit transaction to get appointment ID
      await session.commit()

      # Create Google Calendar event (after DB commit to ensure consistency)
      calendar_service = get_calendar_service()
      event_id = calendar_service.create_event(
        patient_name=patient.name,
        patient_email=patient.email,
        patient_phone=patient.phone,
        reason=i.reason,
        start_time=start_time,
        end_time=end_time,
        appointment_id=appointment.id
      )

      # Update appointment with calendar event ID if created
      if event_id:
        appointment.google_calendar_event_id = event_id
        await session.commit()
        logger.info(f"Linked appointment {appointment.id} to calendar event {event_id}")
      else:
        logger.warning(f"Calendar event not created for appointment {appointment.id} - calendar may be disabled")

      confirmation_id = f"cnf_{appointment.id}_{int(datetime.now().timestamp())}"
      
      # ========================================
      # 📧 SEND CONFIRMATION EMAIL
      # ========================================
      logger.info(f"📧 Attempting to send confirmation email to {patient.email}")
      email_service = get_email_service()
      
      email_sent = email_service.send_appointment_confirmation(
        patient_name=patient.name,
        patient_email=patient.email,
        appointment_date=start_time,
        appointment_time_start=i.slot_start,
        appointment_time_end=i.slot_end,
        reason=i.reason,
        confirmation_id=confirmation_id,
        phone=patient.phone
      )
      
      if email_sent:
        logger.info(f"✅ Confirmation email sent successfully to {patient.email}")
      else:
        logger.warning(f"⚠️  Confirmation email NOT sent (check email configuration)")
      
      logger.info(f"Successfully booked appointment {appointment.id}")
      return BookAppointmentOutput(confirmation_id=confirmation_id)

    except ValueError as e:
      # Conflict detected or validation error
      logger.warning(f"Booking failed: {e}")
      raise
    except Exception as e:
      logger.error(f"Unexpected error during booking: {e}")
      raise

async def lookup_appointment(i: LookupAppointmentInput) -> LookupAppointmentOutput:
  """Lookup appointments by patient name and optional date for verification before cancel/reschedule.
  
  Returns appointments with ANY status (confirmed, cancelled, completed) to allow operations on cancelled appointments.
  """
  i.name = sanitize_name(i.name)
  logger.info(f"Executing lookup_appointment handler for patient: {i.name}")
  async with _session_factory() as session:
    appointment_service = AppointmentService(session)
    
    # Parse date if provided
    target_date = None
    if i.date:
      try:
        target_date = datetime.fromisoformat(i.date.replace("Z", "+00:00"))
      except ValueError:
        logger.warning(f"Invalid date format: {i.date}")
    
    # Find appointments (including cancelled ones)
    if target_date:
      # Look for specific appointment on this date (any status)
      appointment = await appointment_service.find_appointment(i.name, target_date, include_cancelled=True)
      appointments = [appointment] if appointment else []
    else:
      # Get all appointments for this patient (including cancelled)
      now = datetime.now()
      appointments = await appointment_service.get_appointments_for_patient(i.name, now, include_cancelled=True)
    
    # Convert to output format
    appointment_infos = []
    for appt in appointments:
      appointment_infos.append(AppointmentInfo(
        appointment_id=appt.id,
        patient_name=appt.patient.name,
        start_time=appt.start_time.isoformat(),
        end_time=appt.end_time.isoformat(),
        reason=appt.reason,
        status=appt.status
      ))
    
    logger.info(f"Found {len(appointment_infos)} appointments (all statuses) for {i.name}")
    return LookupAppointmentOutput(
      appointments=appointment_infos,
      count=len(appointment_infos)
    )

async def cancel_appointment(i: CancelAppointmentInput) -> CancelAppointmentOutput:
  """Cancel appointment by patient name and time, remove from Google Calendar, and SEND cancellation email."""
  i.name = sanitize_name(i.name)
  logger.info("Executing cancel_appointment handler")
  async with _session_factory() as session:
    appointment_service = AppointmentService(session)

    # Find appointment
    start_time = datetime.fromisoformat(i.slot_start.replace("Z", "+00:00"))
    appointment = await appointment_service.find_appointment(i.name, start_time)

    if not appointment:
      # Provide helpful error message
      logger.warning(f"No appointment found for {i.name} at {i.slot_start}")
      
      # Try to find ANY appointments for this patient to help debug
      now = datetime.now()
      all_appointments = await appointment_service.get_upcoming_appointments_for_patient(i.name, now)
      
      if all_appointments:
        found_times = [appt.start_time.isoformat() for appt in all_appointments[:3]]
        error_msg = f"No appointment found for {i.name} at {i.slot_start}. Found {len(all_appointments)} other appointments: {', '.join(found_times)}"
      else:
        error_msg = f"No appointment found for {i.name} at {i.slot_start}. No appointments found for this patient."
      
      raise ValueError(error_msg)

    # Store info BEFORE canceling (we need it for email)
    calendar_event_id = appointment.google_calendar_event_id
    patient = appointment.patient
    appointment_start = appointment.start_time
    appointment_reason = appointment.reason
    patient_email = patient.email
    patient_name = patient.name

    # Cancel it
    await appointment_service.cancel_appointment(
      appointment_id=appointment.id,
      cancellation_reason=i.reason if i.reason else None
    )
    await session.commit()

    # Delete from Google Calendar
    if calendar_event_id:
      calendar_service = get_calendar_service()
      deleted = calendar_service.delete_event(calendar_event_id)
      if deleted:
        logger.info(f"Deleted calendar event {calendar_event_id} for cancelled appointment {appointment.id}")
      else:
        logger.warning(f"Failed to delete calendar event {calendar_event_id}")
    else:
      logger.info(f"No calendar event linked to appointment {appointment.id}")

    # ========================================
    # 📧 SEND CANCELLATION EMAIL
    # ========================================
    logger.info(f"📧 Attempting to send cancellation email to {patient_email}")
    email_service = get_email_service()
    
    email_sent = email_service.send_cancellation_email(
      patient_name=patient_name,
      patient_email=patient_email,
      appointment_date=appointment_start,
      appointment_time=i.slot_start,
      reason=appointment_reason
    )
    
    if email_sent:
      logger.info(f"✅ Cancellation email sent successfully to {patient_email}")
    else:
      logger.warning(f"⚠️  Cancellation email NOT sent (check email configuration)")

    logger.info(f"Cancelled appointment {appointment.id}")
    return CancelAppointmentOutput(status="cancelled")

async def reschedule_appointment(i: RescheduleAppointmentInput) -> RescheduleAppointmentOutput:
  """Reschedule appointment to new time, update Google Calendar, and SEND reschedule email."""
  i.name = sanitize_name(i.name)
  logger.info("Executing reschedule_appointment handler")
  async with _session_factory() as session:
    appointment_service = AppointmentService(session)

    # Find current appointment (including cancelled ones)
    current_start = datetime.fromisoformat(i.current_slot_start.replace("Z", "+00:00"))
    appointment = await appointment_service.find_appointment(i.name, current_start, include_cancelled=True)

    if not appointment:
      logger.warning(f"Exact appointment not found for {i.name} at {i.current_slot_start}. Searching for any appointments...")
      # Try to find any appointment for this patient (including cancelled)
      all_appointments = await appointment_service.get_appointments_for_patient(i.name, include_cancelled=True)
      if not all_appointments:
        logger.error(f"No appointments found for {i.name}")
        raise ValueError(f"No appointment found for {i.name} at {i.current_slot_start} and no other appointments to reschedule")
      # Use the first appointment as fallback
      appointment = all_appointments[0]
      logger.info(f"Using appointment for {i.name} at {appointment.start_time} (status: {appointment.status}) as fallback")

    # Store OLD appointment info for email
    old_appointment_start = appointment.start_time
    old_appointment_time = i.current_slot_start
    patient = appointment.patient
    appointment_reason = appointment.reason

    # Check if appointment is cancelled
    is_cancelled = appointment.status == "cancelled"
    if is_cancelled:
      logger.info(f"Rescheduling CANCELLED appointment {appointment.id} - will reactivate it")

    # Parse new times
    new_start = datetime.fromisoformat(i.new_slot_start.replace("Z", "+00:00"))
    new_end = datetime.fromisoformat(i.new_slot_end.replace("Z", "+00:00"))
    
    logger.info(f"Rescheduling appointment {appointment.id} from {appointment.start_time.isoformat()} to {new_start.isoformat()}")
    
    # Call the service's reschedule method (it already handles calendar)
    new_appointment = await appointment_service.reschedule_appointment(
      appointment_id=appointment.id,
      new_start_time=new_start,
      new_end_time=new_end
    )
    
    await session.commit()
    logger.info(f"Successfully rescheduled to new appointment {new_appointment.id} at {new_appointment.start_time.isoformat()}")

    new_confirmation_id = f"cnf_{new_appointment.id}_{int(datetime.now().timestamp())}"
    
    status_message = "reactivated and rescheduled" if is_cancelled else "rescheduled"
    logger.info(f"{status_message.capitalize()} appointment {appointment.id} to {new_appointment.id}")

    # ========================================
    # 📧 SEND RESCHEDULE EMAIL
    # ========================================
    logger.info(f"📧 Attempting to send reschedule email to {patient.email}")
    email_service = get_email_service()
    
    email_sent = email_service.send_reschedule_email(
      patient_name=patient.name,
      patient_email=patient.email,
      old_date=old_appointment_start,
      old_time=old_appointment_time,
      new_date=new_start,
      new_time_start=i.new_slot_start,
      new_time_end=i.new_slot_end,
      reason=appointment_reason,
      confirmation_id=new_confirmation_id,
      phone=patient.phone
    )
    
    if email_sent:
      logger.info(f"✅ Reschedule email sent successfully to {patient.email}")
    else:
      logger.warning(f"⚠️  Reschedule email NOT sent (check email configuration)")

    return RescheduleAppointmentOutput(
      status=status_message,
      new_confirmation_id=new_confirmation_id
    )


async def get_upcoming_appointments(i: GetUpcomingAppointmentsInput) -> GetUpcomingAppointmentsOutput:
  """Get all upcoming confirmed appointments for a patient from now onward."""
  i.name = sanitize_name(i.name)
  logger.info(f"Executing get_upcoming_appointments handler for {i.name}")
  async with _session_factory() as session:
    service = AppointmentService(session)

    now = datetime.now()
    appointments = await service.get_upcoming_appointments_for_patient(i.name, now)

    slots: list[Slot] = []
    for appt in appointments:
      slots.append(Slot(start=appt.start_time.isoformat(), end=appt.end_time.isoformat()))

    logger.info(f"Found {len(slots)} upcoming appointments for {i.name}")
    return GetUpcomingAppointmentsOutput(slots=slots)


async def get_hours(i: GetHoursInput) -> GetHoursOutput:
  """Get clinic hours dynamically from database."""
  logger.info("Executing get_hours handler")
  
  async with _session_factory() as session:
    service = AppointmentService(session)
    
    # Get all clinic hours from database
    all_hours = await service.get_all_clinic_hours()
    
    if not all_hours:
      # Fallback if no hours configured
      return GetHoursOutput(hours_text="Clinic hours not configured. Please contact us for availability.")
    
    # Day name mapping
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    short_day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # Build hours text
    hours_parts = []
    for hours in all_hours:
      day_name = short_day_names[hours.day_of_week]
      if hours.is_active:
        start = hours.start_time.strftime("%I:%M%p").lstrip("0").lower()
        end = hours.end_time.strftime("%I:%M%p").lstrip("0").lower()
        
        # Add break info if exists
        if hours.break_start and hours.break_end:
          break_start = hours.break_start.strftime("%I:%M%p").lstrip("0").lower()
          break_end = hours.break_end.strftime("%I:%M%p").lstrip("0").lower()
          hours_parts.append(f"{day_name}: {start}-{end} (break {break_start}-{break_end})")
        else:
          hours_parts.append(f"{day_name}: {start}-{end}")
      else:
        hours_parts.append(f"{day_name}: closed")
    
    hours_text = "; ".join(hours_parts)
    
    # Add upcoming holidays info
    upcoming_holidays = await service.get_all_holidays()
    if upcoming_holidays:
      # Filter for future holidays only
      today = datetime.now().date()
      future_holidays = [h for h in upcoming_holidays if h.date >= today]
      if future_holidays and len(future_holidays) <= 3:
        holiday_info = ", ".join([f"{h.name} ({h.date.strftime('%b %d')})" for h in future_holidays[:3]])
        hours_text += f". Upcoming closures: {holiday_info}"
    
    return GetHoursOutput(hours_text=hours_text)


async def get_location(i: GetLocationInput) -> GetLocationOutput:
  logger.info("Executing get_location handler")
  return GetLocationOutput(address_text="123 Clinic Way, Suite 200, Springfield, ST")


async def get_insurance_supported(i: GetInsuranceSupportedInput) -> GetInsuranceSupportedOutput:
  logger.info("Executing get_insurance_supported handler")
  accepted = i.provider.lower() in {"aetna","blue cross","cigna","united"}
  return GetInsuranceSupportedOutput(accepted=accepted)


async def escalate_to_human(i: EscalateToHumanInput) -> EscalateToHumanOutput:
  logger.info("Executing escalate_to_human handler")
  return EscalateToHumanOutput(status="queued")


async def send_confirmation(i: SendConfirmationInput) -> SendConfirmationOutput:
  if i.channel == "email":
    i.address = sanitize_email(i.address)
  logger.info(f"Executing send_confirmation handler to {i.channel}: {i.address}")
  return SendConfirmationOutput(status="sent")


def register_handlers(router: ToolRouter, session_factory=None) -> None:
  """Register all appointment handlers with database session."""
  if session_factory:
    set_session_factory(session_factory)

  router.register("check_availability", CheckAvailabilityInput, CheckAvailabilityOutput, check_availability)
  router.register("book_appointment", BookAppointmentInput, BookAppointmentOutput, book_appointment)
  router.register("lookup_appointment", LookupAppointmentInput, LookupAppointmentOutput, lookup_appointment)
  router.register("cancel_appointment", CancelAppointmentInput, CancelAppointmentOutput, cancel_appointment)
  router.register("reschedule_appointment", RescheduleAppointmentInput, RescheduleAppointmentOutput, reschedule_appointment)
  router.register("get_upcoming_appointments", GetUpcomingAppointmentsInput, GetUpcomingAppointmentsOutput, get_upcoming_appointments)
  router.register("get_hours", GetHoursInput, GetHoursOutput, get_hours)
  router.register("get_location", GetLocationInput, GetLocationOutput, get_location)
  router.register("get_insurance_supported", GetInsuranceSupportedInput, GetInsuranceSupportedOutput, get_insurance_supported)
  router.register("escalate_to_human", EscalateToHumanInput, EscalateToHumanOutput, escalate_to_human)
  router.register("send_confirmation", SendConfirmationInput, SendConfirmationOutput, send_confirmation)

  logger.info("Registered 11 appointment handlers with database integration")