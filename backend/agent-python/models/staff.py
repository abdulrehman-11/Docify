"""
Staff model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, func
from .base import Base


class Staff(Base):
    """Staff member model for clinic staff management"""
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="staff", nullable=False)  # "staff", "admin"
    
    # Permissions stored as JSON
    # Example: {"view_appointments": true, "manage_appointments": true, "view_patients": true, "manage_patients": false}
    permissions = Column(JSON, default={}, nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(Integer, nullable=True)  # Admin ID who created this staff
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Staff(id={self.id}, name={self.name}, email={self.email}, role={self.role})>"
