from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Literal, Optional
from datetime import datetime


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

  @field_validator("slot_start", mode="before")
  @classmethod
  def _valid_slot_start(cls, v: str) -> str:
    return ensure_iso8601(v)

  @field_validator("slot_end", mode="before")
  @classmethod
  def _valid_slot_end(cls, v: str) -> str:
    return ensure_iso8601(v)


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


