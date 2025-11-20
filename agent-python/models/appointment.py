from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Index,
    Date,
    Time,
)
from sqlalchemy.orm import relationship
from database import Base
from models.base import TimestampMixin
import enum

class AppointmentStatus(enum.Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"
    COMPLETED = "COMPLETED"

class Appointment(Base, TimestampMixin):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    # Denormalized contact fields to satisfy frontend requirements and facilitate lookups
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    date = Column(Date, nullable=False, index=True)
    day = Column(String(16), nullable=False)
    time = Column(Time(timezone=True), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(SQLEnum(AppointmentStatus), nullable=False, default=AppointmentStatus.CONFIRMED, index=True)
    cancellation_reason = Column(Text, nullable=True)

    # Relationship
    patient = relationship("Patient", backref="appointments")

    # Composite index for availability queries
    __table_args__ = (
        Index('idx_appointments_start_status', 'start_time', 'status'),
    )

    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, start={self.start_time}, status={self.status})>"
