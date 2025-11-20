from sqlalchemy import Column, Integer, Time, Boolean, DateTime, CheckConstraint
from sqlalchemy.sql import func
from database import Base

class ClinicHours(Base):
    __tablename__ = "clinic_hours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)  # e.g., 09:00:00
    end_time = Column(Time, nullable=False)  # e.g., 17:00:00
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint('day_of_week >= 0 AND day_of_week <= 6', name='valid_day_of_week'),
    )

    def __repr__(self):
        return f"<ClinicHours(day={self.day_of_week}, {self.start_time}-{self.end_time})>"
