import logging
from .schemas import (
  CheckAvailabilityInput, CheckAvailabilityOutput,
  Slot,
  BookAppointmentInput, BookAppointmentOutput,
  CancelAppointmentInput, CancelAppointmentOutput,
  RescheduleAppointmentInput, RescheduleAppointmentOutput,
  GetHoursInput, GetHoursOutput,
  GetLocationInput, GetLocationOutput,
  GetInsuranceSupportedInput, GetInsuranceSupportedOutput,
  EscalateToHumanInput, EscalateToHumanOutput,
  SendConfirmationInput, SendConfirmationOutput,
)
from .router import ToolRouter
from datetime import datetime, timedelta
from services.appointment_service import AppointmentService
from services.patient_service import PatientService
from services.google_calendar_service import get_calendar_service

logger = logging.getLogger(__name__)

# Session factory will be passed from agent.py
_session_factory = None

def set_session_factory(factory):
    """Set the database session factory."""
    global _session_factory
    _session_factory = factory


async def check_availability(i: CheckAvailabilityInput) -> CheckAvailabilityOutput:
  """Check available appointment slots within time window."""
  logger.info("Executing check_availability handler")
  async with _session_factory() as session:
    service = AppointmentService(session)

    # Parse preferred time window
    start_time = datetime.fromisoformat(i.preferred_time_window.from_.replace("Z", "+00:00"))
    end_time = datetime.fromisoformat(i.preferred_time_window.to.replace("Z", "+00:00"))

    slots = await service.check_availability(start_time, end_time)
    logger.info(f"Found {len(slots)} available slots for '{i.reason}'")

    # Debug logging: Show slot times in readable format for troubleshooting
    if slots:
      slot_times = [slot["start"][11:16] for slot in slots[:5]]  # Show first 5 times (HH:MM format)
      logger.info(f"Sample slot times (HH:MM): {', '.join(slot_times)}")

    return CheckAvailabilityOutput(slots=[
      Slot(start=slot["start"], end=slot["end"]) for slot in slots
    ])


async def book_appointment(i: BookAppointmentInput) -> BookAppointmentOutput:
  """Book appointment with conflict detection and Google Calendar integration."""
  logger.info("Executing book_appointment handler")
  logger.info(f"Booking details - Name: {i.name}, Email: {i.email}, Slot: {i.slot_start[11:16]}-{i.slot_end[11:16]}")

  async with _session_factory() as session:
    try:
      # Find or create patient
      patient_service = PatientService(session)
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
      logger.info(f"Successfully booked appointment {appointment.id}")
      return BookAppointmentOutput(confirmation_id=confirmation_id)

    except ValueError as e:
      # Conflict detected or validation error
      logger.warning(f"Booking failed: {e}")
      raise
    except Exception as e:
      logger.error(f"Unexpected error during booking: {e}")
      raise


async def cancel_appointment(i: CancelAppointmentInput) -> CancelAppointmentOutput:
  """Cancel appointment by patient name and time, and remove from Google Calendar."""
  logger.info("Executing cancel_appointment handler")
  async with _session_factory() as session:
    appointment_service = AppointmentService(session)

    # Find appointment
    start_time = datetime.fromisoformat(i.slot_start.replace("Z", "+00:00"))
    appointment = await appointment_service.find_appointment(i.name, start_time)

    if not appointment:
      raise ValueError(f"No appointment found for {i.name} at {i.slot_start}")

    # Store calendar event ID before canceling
    calendar_event_id = appointment.google_calendar_event_id

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

    logger.info(f"Cancelled appointment {appointment.id}")
    return CancelAppointmentOutput(status="cancelled")


async def reschedule_appointment(i: RescheduleAppointmentInput) -> RescheduleAppointmentOutput:
  """Reschedule appointment to new time and update Google Calendar."""
  logger.info("Executing reschedule_appointment handler")
  async with _session_factory() as session:
    appointment_service = AppointmentService(session)

    # Find current appointment
    current_start = datetime.fromisoformat(i.current_slot_start.replace("Z", "+00:00"))
    appointment = await appointment_service.find_appointment(i.name, current_start)

    if not appointment:
      raise ValueError(f"No appointment found for {i.name} at {i.current_slot_start}")

    # Store old calendar event ID
    old_calendar_event_id = appointment.google_calendar_event_id

    # Get patient info for calendar event
    patient = appointment.patient

    # Reschedule atomically
    new_start = datetime.fromisoformat(i.new_slot_start.replace("Z", "+00:00"))
    new_end = datetime.fromisoformat(i.new_slot_end.replace("Z", "+00:00"))
    new_appointment = await appointment_service.reschedule_appointment(
      appointment_id=appointment.id,
      new_start_time=new_start,
      new_end_time=new_end
    )
    await session.commit()

    # Handle Google Calendar update
    calendar_service = get_calendar_service()
    
    if old_calendar_event_id:
      # Update the existing calendar event with new times
      updated = calendar_service.update_event(
        event_id=old_calendar_event_id,
        patient_name=patient.name,
        patient_email=patient.email,
        patient_phone=patient.phone,
        reason=new_appointment.reason,
        start_time=new_start,
        end_time=new_end,
        appointment_id=new_appointment.id
      )
      
      if updated:
        # Transfer the calendar event ID to new appointment
        new_appointment.google_calendar_event_id = old_calendar_event_id
        await session.commit()
        logger.info(f"Updated calendar event {old_calendar_event_id} for rescheduled appointment")
      else:
        # Create a new event if update failed
        logger.warning(f"Failed to update calendar event, creating new one")
        new_event_id = calendar_service.create_event(
          patient_name=patient.name,
          patient_email=patient.email,
          patient_phone=patient.phone,
          reason=new_appointment.reason,
          start_time=new_start,
          end_time=new_end,
          appointment_id=new_appointment.id
        )
        if new_event_id:
          new_appointment.google_calendar_event_id = new_event_id
          await session.commit()
    else:
      # No existing calendar event, create new one
      new_event_id = calendar_service.create_event(
        patient_name=patient.name,
        patient_email=patient.email,
        patient_phone=patient.phone,
        reason=new_appointment.reason,
        start_time=new_start,
        end_time=new_end,
        appointment_id=new_appointment.id
      )
      if new_event_id:
        new_appointment.google_calendar_event_id = new_event_id
        await session.commit()
        logger.info(f"Created new calendar event {new_event_id} for rescheduled appointment")

    new_confirmation_id = f"cnf_{new_appointment.id}_{int(datetime.now().timestamp())}"
    logger.info(f"Rescheduled appointment {appointment.id} to {new_appointment.id}")

    return RescheduleAppointmentOutput(
      status="rescheduled",
      new_confirmation_id=new_confirmation_id
    )


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
  logger.info("Executing send_confirmation handler")
  return SendConfirmationOutput(status="sent")


def register_handlers(router: ToolRouter, session_factory=None) -> None:
  """Register all appointment handlers with database session."""
  if session_factory:
    set_session_factory(session_factory)

  router.register("check_availability", CheckAvailabilityInput, CheckAvailabilityOutput, check_availability)
  router.register("book_appointment", BookAppointmentInput, BookAppointmentOutput, book_appointment)
  router.register("cancel_appointment", CancelAppointmentInput, CancelAppointmentOutput, cancel_appointment)
  router.register("reschedule_appointment", RescheduleAppointmentInput, RescheduleAppointmentOutput, reschedule_appointment)
  router.register("get_hours", GetHoursInput, GetHoursOutput, get_hours)
  router.register("get_location", GetLocationInput, GetLocationOutput, get_location)
  router.register("get_insurance_supported", GetInsuranceSupportedInput, GetInsuranceSupportedOutput, get_insurance_supported)
  router.register("escalate_to_human", EscalateToHumanInput, EscalateToHumanOutput, escalate_to_human)
  router.register("send_confirmation", SendConfirmationInput, SendConfirmationOutput, send_confirmation)

  logger.info("Registered 9 appointment handlers with database integration")

