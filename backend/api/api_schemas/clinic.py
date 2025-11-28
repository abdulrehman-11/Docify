"""
Pydantic schemas for Clinic Hours and Dashboard API endpoints.
"""
from pydantic import BaseModel, Field, field_serializer
from datetime import time, datetime
from datetime import date as date_type
from typing import Optional, List


# Clinic Hours schemas
class ClinicHoursResponse(BaseModel):
    """Schema for clinic hours response."""
    id: int
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    start_time: time
    end_time: time
    is_active: bool
    break_start: Optional[time] = None
    break_end: Optional[time] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_serializer('start_time', 'end_time', 'break_start', 'break_end')
    def serialize_time(self, value: time) -> Optional[str]:
        """Serialize time to string format."""
        return value.strftime('%H:%M:%S') if value else None
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> Optional[str]:
        """Serialize datetime to ISO format string."""
        return value.isoformat() if value else None

    class Config:
        from_attributes = True


class ClinicHoursUpdate(BaseModel):
    """Schema for updating clinic hours."""
    start_time: Optional[time] = Field(None, description="Opening time")
    end_time: Optional[time] = Field(None, description="Closing time")
    is_active: Optional[bool] = Field(None, description="Whether clinic is open this day")
    break_start: Optional[time] = Field(None, description="Break start time (e.g., lunch)")
    break_end: Optional[time] = Field(None, description="Break end time")


class ClinicHoursCreate(BaseModel):
    """Schema for creating clinic hours."""
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    start_time: time = Field(..., description="Opening time")
    end_time: time = Field(..., description="Closing time")
    is_active: bool = Field(True, description="Whether clinic is open this day")
    break_start: Optional[time] = Field(None, description="Break start time")
    break_end: Optional[time] = Field(None, description="Break end time")


class ClinicHoursBulkUpdate(BaseModel):
    """Schema for bulk updating clinic hours (apply to multiple days)."""
    day_of_weeks: List[int] = Field(..., description="List of days to update (0=Monday, 6=Sunday)")
    start_time: Optional[time] = Field(None, description="Opening time")
    end_time: Optional[time] = Field(None, description="Closing time")
    is_active: Optional[bool] = Field(None, description="Whether clinic is open")
    break_start: Optional[time] = Field(None, description="Break start time")
    break_end: Optional[time] = Field(None, description="Break end time")


# Clinic Holiday schemas
class ClinicHolidayResponse(BaseModel):
    """Schema for clinic holiday response."""
    id: int
    date: date_type
    name: str
    is_full_day: bool
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    created_at: datetime
    created_by: Optional[str] = None

    @field_serializer('date')
    def serialize_date(self, value: date_type) -> str:
        """Serialize date to string format."""
        return value.isoformat() if value else None

    @field_serializer('start_time', 'end_time')
    def serialize_time(self, value: time) -> Optional[str]:
        """Serialize time to string format."""
        return value.strftime('%H:%M:%S') if value else None

    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> Optional[str]:
        """Serialize datetime to ISO format string."""
        return value.isoformat() if value else None

    class Config:
        from_attributes = True


class ClinicHolidayCreate(BaseModel):
    """Schema for creating a clinic holiday."""
    date: date_type = Field(..., description="The date of the holiday")
    name: str = Field(..., min_length=1, max_length=255, description="Name of the holiday")
    is_full_day: bool = Field(True, description="Whether it's a full day off")
    start_time: Optional[time] = Field(None, description="Custom opening time if not full day off")
    end_time: Optional[time] = Field(None, description="Custom closing time if not full day off")


class ClinicHolidayUpdate(BaseModel):
    """Schema for updating a clinic holiday."""
    date: Optional[date_type] = Field(None, description="The date of the holiday")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the holiday")
    is_full_day: Optional[bool] = Field(None, description="Whether it's a full day off")
    start_time: Optional[time] = Field(None, description="Custom opening time if not full day off")
    end_time: Optional[time] = Field(None, description="Custom closing time if not full day off")


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
