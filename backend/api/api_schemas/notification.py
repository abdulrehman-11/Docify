"""
Notification schemas for API requests/responses.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class NotificationTypeEnum(str, Enum):
    """Notification type enum for API"""
    APPOINTMENT_CREATED = "APPOINTMENT_CREATED"
    APPOINTMENT_UPDATED = "APPOINTMENT_UPDATED"
    APPOINTMENT_CANCELLED = "APPOINTMENT_CANCELLED"
    APPOINTMENT_RESCHEDULED = "APPOINTMENT_RESCHEDULED"
    APPOINTMENT_UPCOMING = "APPOINTMENT_UPCOMING"
    CLINIC_HOURS_UPDATED = "CLINIC_HOURS_UPDATED"
    SYSTEM = "SYSTEM"


class NotificationCreate(BaseModel):
    """Schema for creating a notification"""
    user_role: Optional[str] = None
    staff_id: Optional[int] = None
    type: NotificationTypeEnum
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    data: Optional[Dict[str, Any]] = None


class NotificationUpdate(BaseModel):
    """Schema for updating notification (mainly marking as read)"""
    is_read: bool


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: int
    user_role: Optional[str]
    staff_id: Optional[int]
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]]
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list"""
    notifications: list[NotificationResponse]
    total: int
    unread_count: int
