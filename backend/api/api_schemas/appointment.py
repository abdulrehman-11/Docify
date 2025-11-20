"""
Pydantic schemas for Appointment API endpoints.
"""
from pydantic import BaseModel, Field, field_serializer, field_validator
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class AppointmentStatus(str, Enum):
    """Appointment status enum."""
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"
    COMPLETED = "COMPLETED"


# Request schemas
class AppointmentCreate(BaseModel):
    """Schema for creating a new appointment."""
    patient_id: int = Field(..., gt=0, description="Patient ID")
    start_time: datetime = Field(..., description="Appointment start time (ISO8601)")
    end_time: datetime = Field(..., description="Appointment end time (ISO8601)")
    reason: str = Field(..., min_length=1, description="Reason for visit")
    
    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def ensure_utc_timezone(cls, value):
        """Ensure datetime has UTC timezone. If naive, assume it's UTC."""
        if isinstance(value, str):
            # Parse string to datetime
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        elif isinstance(value, datetime):
            dt = value
        else:
            raise ValueError(f"Invalid datetime value: {value}")
        
        # If naive (no timezone), treat as UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment."""
    start_time: Optional[datetime] = Field(None, description="New appointment start time")
    end_time: Optional[datetime] = Field(None, description="New appointment end time")
    reason: Optional[str] = Field(None, min_length=1, description="Reason for visit")
    status: Optional[AppointmentStatus] = Field(None, description="Appointment status")
    cancellation_reason: Optional[str] = Field(None, description="Reason for cancellation")
    
    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def ensure_utc_timezone(cls, value):
        """Ensure datetime has UTC timezone. If naive, assume it's UTC."""
        if value is None:
            return value
            
        if isinstance(value, str):
            # Parse string to datetime
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        elif isinstance(value, datetime):
            dt = value
        else:
            raise ValueError(f"Invalid datetime value: {value}")
        
        # If naive (no timezone), treat as UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt


class AppointmentCancel(BaseModel):
    """Schema for canceling an appointment."""
    cancellation_reason: Optional[str] = Field(None, description="Reason for cancellation")


class AvailabilityRequest(BaseModel):
    """Schema for checking appointment availability."""
    start_date: datetime = Field(..., description="Start of time window")
    end_date: datetime = Field(..., description="End of time window")


# Response schemas
class AppointmentResponse(BaseModel):
    """Schema for appointment response."""
    id: int
    patient_id: int
    start_time: datetime
    end_time: datetime
    reason: str
    status: str
    cancellation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    @field_serializer('start_time', 'end_time', 'created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime to ISO format string with UTC timezone."""
        if value is None:
            return None
        # Ensure timezone-aware datetime (assume UTC if naive)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    class Config:
        from_attributes = True


class AppointmentWithPatientResponse(BaseModel):
    """Schema for appointment response with patient details."""
    id: int
    patient_id: int
    patient_name: str
    patient_email: str
    patient_phone: str
    start_time: datetime
    end_time: datetime
    reason: str
    status: str
    cancellation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    @field_serializer('start_time', 'end_time', 'created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime to ISO format string with UTC timezone."""
        if value is None:
            return None
        # Ensure timezone-aware datetime (assume UTC if naive)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    class Config:
        from_attributes = True


class AppointmentListResponse(BaseModel):
    """Schema for paginated appointment list."""
    total: int
    page: int
    page_size: int
    appointments: list[AppointmentWithPatientResponse]


class AvailabilitySlot(BaseModel):
    """Schema for available time slot."""
    start: str
    end: str


class AvailabilityResponse(BaseModel):
    """Schema for availability check response."""
    slots: list[AvailabilitySlot]
