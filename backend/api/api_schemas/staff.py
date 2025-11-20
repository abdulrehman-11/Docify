"""
Staff schemas for API
"""
from pydantic import BaseModel, EmailStr, field_serializer
from datetime import datetime
from typing import Optional, Dict, Any


class StaffBase(BaseModel):
    """Base staff schema"""
    name: str
    email: EmailStr
    role: str = "staff"
    permissions: Dict[str, bool] = {}


class StaffCreate(StaffBase):
    """Schema for creating a staff member"""
    password: str


class StaffUpdate(BaseModel):
    """Schema for updating a staff member"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[Dict[str, bool]] = None
    is_active: Optional[bool] = None


class StaffResponse(StaffBase):
    """Schema for staff response"""
    id: int
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """Serialize datetime to ISO format string"""
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True


class StaffListResponse(BaseModel):
    """Schema for paginated staff list"""
    total: int
    page: int
    page_size: int
    staff: list[StaffResponse]


class StaffLogin(BaseModel):
    """Schema for staff login"""
    email: EmailStr
    password: str


class StaffLoginResponse(BaseModel):
    """Schema for staff login response"""
    access_token: str
    token_type: str = "bearer"
    user: StaffResponse
