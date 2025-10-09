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


def register_handlers(router: ToolRouter) -> None:
  router.register(
    "check_availability",
    CheckAvailabilityInput, CheckAvailabilityOutput,
    lambda i: CheckAvailabilityOutput(slots=[
      Slot(start=i.preferred_time_window.from_, end=(datetime.fromisoformat(i.preferred_time_window.from_.replace("Z","+00:00")) + timedelta(minutes=30)).isoformat())
    ])
  )

  router.register(
    "book_appointment",
    BookAppointmentInput, BookAppointmentOutput,
    lambda i: BookAppointmentOutput(confirmation_id=f"cnf_{int(datetime.now().timestamp())}")
  )

  router.register(
    "cancel_appointment",
    CancelAppointmentInput, CancelAppointmentOutput,
    lambda i: CancelAppointmentOutput(status="cancelled")
  )

  router.register(
    "reschedule_appointment",
    RescheduleAppointmentInput, RescheduleAppointmentOutput,
    lambda i: RescheduleAppointmentOutput(status="rescheduled", new_confirmation_id=f"cnf_{int(datetime.now().timestamp())}")
  )

  router.register(
    "get_hours",
    GetHoursInput, GetHoursOutput,
    lambda i: GetHoursOutput(hours_text="Mon–Fri 8am–6pm; Sat 9am–1pm; Sun closed")
  )

  router.register(
    "get_location",
    GetLocationInput, GetLocationOutput,
    lambda i: GetLocationOutput(address_text="123 Clinic Way, Suite 200, Springfield, ST")
  )

  def insurance_handler(i: GetInsuranceSupportedInput) -> GetInsuranceSupportedOutput:
    accepted = i.provider.lower() in {"aetna","blue cross","cigna","united"}
    return GetInsuranceSupportedOutput(accepted=accepted)

  router.register(
    "get_insurance_supported",
    GetInsuranceSupportedInput, GetInsuranceSupportedOutput,
    insurance_handler
  )

  router.register(
    "escalate_to_human",
    EscalateToHumanInput, EscalateToHumanOutput,
    lambda i: EscalateToHumanOutput(status="queued")
  )

  router.register(
    "send_confirmation",
    SendConfirmationInput, SendConfirmationOutput,
    lambda i: SendConfirmationOutput(status="sent")
  )


