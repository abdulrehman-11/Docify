"""
Notification Model for system-wide notifications.
"""
import sys
from pathlib import Path

# Add agent-python to path
backend_dir = Path(__file__).parent.parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from models.base import Base
import enum


class NotificationType(str, enum.Enum):
    """Types of notifications"""
    APPOINTMENT_CREATED = "APPOINTMENT_CREATED"
    APPOINTMENT_UPDATED = "APPOINTMENT_UPDATED"
    APPOINTMENT_CANCELLED = "APPOINTMENT_CANCELLED"
    APPOINTMENT_RESCHEDULED = "APPOINTMENT_RESCHEDULED"
    APPOINTMENT_UPCOMING = "APPOINTMENT_UPCOMING"
    CLINIC_HOURS_UPDATED = "CLINIC_HOURS_UPDATED"
    SYSTEM = "SYSTEM"


class Notification(Base):
    """Notification model for tracking system notifications"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    
    # User context (null means all users/roles can see)
    user_role = Column(String(50), nullable=True)  # 'admin', 'staff', null = all
    staff_id = Column(Integer, nullable=True)  # specific staff member if applicable
    
    # Notification details
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Additional data (JSON for flexibility)
    data = Column(JSON, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.type}, title='{self.title}', is_read={self.is_read})>"
