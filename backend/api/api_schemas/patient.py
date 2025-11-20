"""
Pydantic schemas for Patient API endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# Request schemas
class PatientCreate(BaseModel):
    """Schema for creating a new patient."""
    name: str = Field(..., min_length=1, max_length=255, description="Patient full name")
    email: EmailStr = Field(..., description="Patient email address (unique)")
    phone: str = Field(..., min_length=10, max_length=20, description="Patient phone number")
    insurance_provider: Optional[str] = Field(None, max_length=255, description="Insurance provider name")


class PatientUpdate(BaseModel):
    """Schema for updating patient information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Patient full name")
    email: Optional[EmailStr] = Field(None, description="Patient email address")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, description="Patient phone number")
    insurance_provider: Optional[str] = Field(None, max_length=255, description="Insurance provider name")


# Response schemas
class PatientResponse(BaseModel):
    """Schema for patient response."""
    id: int
    name: str
    email: str
    phone: str
    insurance_provider: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class PatientListResponse(BaseModel):
    """Schema for paginated patient list."""
    total: int
    page: int
    page_size: int
    patients: list[PatientResponse]
