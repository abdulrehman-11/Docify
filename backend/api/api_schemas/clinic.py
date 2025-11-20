"""
Pydantic schemas for Clinic Hours and Dashboard API endpoints.
"""
from pydantic import BaseModel, Field, field_serializer
from datetime import time, datetime
from typing import Optional


# Clinic Hours schemas
class ClinicHoursResponse(BaseModel):
    """Schema for clinic hours response."""
    id: int
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    start_time: time
    end_time: time
    is_active: bool
    created_at: datetime

    @field_serializer('start_time', 'end_time')
    def serialize_time(self, value: time) -> str:
        """Serialize time to string format."""
        return value.strftime('%H:%M:%S') if value else None
    
    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat() if value else None

    class Config:
        from_attributes = True


class ClinicHoursUpdate(BaseModel):
    """Schema for updating clinic hours."""
    start_time: Optional[time] = Field(None, description="Opening time")
    end_time: Optional[time] = Field(None, description="Closing time")
    is_active: Optional[bool] = Field(None, description="Whether clinic is open this day")


class ClinicHoursCreate(BaseModel):
    """Schema for creating clinic hours."""
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    start_time: time = Field(..., description="Opening time")
    end_time: time = Field(..., description="Closing time")
    is_active: bool = Field(True, description="Whether clinic is open this day")


# Dashboard schemas
class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""
    total_appointments_today: int
    total_appointments_upcoming: int
    total_patients: int
    confirmed_appointments: int
    cancelled_appointments: int
    completed_appointments: int


class TodayAppointment(BaseModel):
    """Schema for today's appointment summary."""
    id: int
    patient_name: str
    patient_phone: str
    start_time: datetime
    end_time: datetime
    reason: str
    status: str

    @field_serializer('start_time', 'end_time')
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat() if value else None

    class Config:
        from_attributes = True


class UpcomingAppointment(BaseModel):
    """Schema for upcoming appointment summary."""
    id: int
    patient_name: str
    patient_email: str
    patient_phone: str
    start_time: datetime
    end_time: datetime
    reason: str
    status: str

    @field_serializer('start_time', 'end_time')
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat() if value else None

    class Config:
        from_attributes = True
