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

logger = logging.getLogger(__name__)


async def check_availability(i: CheckAvailabilityInput) -> CheckAvailabilityOutput:
  logger.info("Executing check_availability handler")
  return CheckAvailabilityOutput(slots=[
    Slot(start=i.preferred_time_window.from_, end=(datetime.fromisoformat(i.preferred_time_window.from_.replace("Z","+00:00")) + timedelta(minutes=30)).isoformat())
  ])


async def book_appointment(i: BookAppointmentInput) -> BookAppointmentOutput:
  logger.info("Executing book_appointment handler")
  return BookAppointmentOutput(confirmation_id=f"cnf_{int(datetime.now().timestamp())}")


async def cancel_appointment(i: CancelAppointmentInput) -> CancelAppointmentOutput:
  logger.info("Executing cancel_appointment handler")
  return CancelAppointmentOutput(status="cancelled")


async def reschedule_appointment(i: RescheduleAppointmentInput) -> RescheduleAppointmentOutput:
  logger.info("Executing reschedule_appointment handler")
  return RescheduleAppointmentOutput(status="rescheduled", new_confirmation_id=f"cnf_{int(datetime.now().timestamp())}")


async def get_hours(i: GetHoursInput) -> GetHoursOutput:
  logger.info("Executing get_hours handler")
  return GetHoursOutput(hours_text="Mon–Fri 8am–6pm; Sat 9am–1pm; Sun closed")


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


def register_handlers(router: ToolRouter) -> None:
  router.register("check_availability", CheckAvailabilityInput, CheckAvailabilityOutput, check_availability)
  router.register("book_appointment", BookAppointmentInput, BookAppointmentOutput, book_appointment)
  router.register("cancel_appointment", CancelAppointmentInput, CancelAppointmentOutput, cancel_appointment)
  router.register("reschedule_appointment", RescheduleAppointmentInput, RescheduleAppointmentOutput, reschedule_appointment)
  router.register("get_hours", GetHoursInput, GetHoursOutput, get_hours)
  router.register("get_location", GetLocationInput, GetLocationOutput, get_location)
  router.register("get_insurance_supported", GetInsuranceSupportedInput, GetInsuranceSupportedOutput, get_insurance_supported)
  router.register("escalate_to_human", EscalateToHumanInput, EscalateToHumanOutput, escalate_to_human)
  router.register("send_confirmation", SendConfirmationInput, SendConfirmationOutput, send_confirmation)