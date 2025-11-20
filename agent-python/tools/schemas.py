from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Literal, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.email_normalizer import normalize_email


def ensure_iso8601(value: str) -> str:
  # pydantic v2: parse to validate
  datetime.fromisoformat(value.replace("Z", "+00:00"))
  return value


class TimeWindow(BaseModel):
  from_: str
  to: str

  @field_validator("from_", mode="before")
  @classmethod
  def _valid_from(cls, v: str) -> str:
    return ensure_iso8601(v)

  @field_validator("to", mode="before")
  @classmethod
  def _valid_to(cls, v: str) -> str:
    return ensure_iso8601(v)


class Slot(BaseModel):
  start: str
  end: str

  @field_validator("start", mode="before")
  @classmethod
  def _valid_start(cls, v: str) -> str:
    return ensure_iso8601(v)

  @field_validator("end", mode="before")
  @classmethod
  def _valid_end(cls, v: str) -> str:
    return ensure_iso8601(v)


class CheckAvailabilityInput(BaseModel):
  reason: str
  preferred_time_window: TimeWindow


class CheckAvailabilityOutput(BaseModel):
  slots: List[Slot]


class BookAppointmentInput(BaseModel):
  name: str
  reason: str
  slot_start: str
  slot_end: str
  insurance: Optional[str]
  phone: str
  email: EmailStr

  @field_validator("email", mode="before")
  @classmethod
  def _normalize_email(cls, v: str) -> str:
    """Normalize spoken email format to proper email address."""
    if not isinstance(v, str):
      return v
    return normalize_email(v)

  @field_validator("slot_start", mode="before")
  @classmethod
  def _valid_slot_start(cls, v: str) -> str:
    iso_str = ensure_iso8601(v)
    # Validate slot_start is in the future
    slot_time = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    now = datetime.now(slot_time.tzinfo) if slot_time.tzinfo else datetime.now()
    if slot_time <= now:
      raise ValueError(f"slot_start must be in the future. Received: {iso_str}, Current time: {now.isoformat()}")
    return iso_str

  @field_validator("slot_end", mode="before")
  @classmethod
  def _valid_slot_end(cls, v: str) -> str:
    return ensure_iso8601(v)

  @field_validator("slot_end")
  @classmethod
  def _validate_duration(cls, slot_end: str, info) -> str:
    """Validate that slot_end is exactly 30 minutes after slot_start."""
    slot_start = info.data.get("slot_start")
    if not slot_start:
      return slot_end

    start_dt = datetime.fromisoformat(slot_start.replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(slot_end.replace("Z", "+00:00"))

    duration = (end_dt - start_dt).total_seconds() / 60  # minutes

    if duration != 30:
      raise ValueError(
        f"Appointment duration must be exactly 30 minutes. "
        f"Got {duration} minutes (start: {slot_start}, end: {slot_end}). "
        f"TIP: Use the exact slot times from check_availability results."
      )

    return slot_end


class BookAppointmentOutput(BaseModel):
  confirmation_id: str


class CancelAppointmentInput(BaseModel):
  name: str
  slot_start: str
  reason: Optional[str]

  @field_validator("slot_start", mode="before")
  @classmethod
  def _valid_slot_start(cls, v: str) -> str:
    return ensure_iso8601(v)


class CancelAppointmentOutput(BaseModel):
  status: Literal["cancelled"]


class RescheduleAppointmentInput(BaseModel):
  name: str
  current_slot_start: str
  new_slot_start: str
  new_slot_end: str

  @field_validator("current_slot_start", mode="before")
  @classmethod
  def _valid_current(cls, v: str) -> str:
    return ensure_iso8601(v)

  @field_validator("new_slot_start", mode="before")
  @classmethod
  def _valid_new_start(cls, v: str) -> str:
    return ensure_iso8601(v)

  @field_validator("new_slot_end", mode="before")
  @classmethod
  def _valid_new_end(cls, v: str) -> str:
    return ensure_iso8601(v)


class RescheduleAppointmentOutput(BaseModel):
  status: Literal["rescheduled"]
  new_confirmation_id: str


class GetHoursInput(BaseModel):
  pass


class GetHoursOutput(BaseModel):
  hours_text: str


class GetLocationInput(BaseModel):
  pass


class GetLocationOutput(BaseModel):
  address_text: str


class GetInsuranceSupportedInput(BaseModel):
  provider: str


class GetInsuranceSupportedOutput(BaseModel):
  accepted: bool


class EscalateToHumanInput(BaseModel):
  reason: str
  callback_number: Optional[str]


class EscalateToHumanOutput(BaseModel):
  status: Literal["connected", "queued"]


class SendConfirmationInput(BaseModel):
  channel: Literal["sms", "email"]
  address: str
  message: str


class SendConfirmationOutput(BaseModel):
  status: Literal["sent"]


