from sqlalchemy import Column, Integer, Time, Boolean, DateTime, CheckConstraint, Date, String
from sqlalchemy.sql import func
from database import Base


class ClinicHours(Base):
    """Regular weekly clinic hours for each day of week."""
    __tablename__ = "clinic_hours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)  # e.g., 09:00:00
    end_time = Column(Time, nullable=False)  # e.g., 17:00:00
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Break time fields
    break_start = Column(Time, nullable=True)  # e.g., 12:00:00 for lunch break
    break_end = Column(Time, nullable=True)    # e.g., 13:00:00 end of lunch break
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint('day_of_week >= 0 AND day_of_week <= 6', name='valid_day_of_week'),
    )

    def __repr__(self):
        return f"<ClinicHours(day={self.day_of_week}, {self.start_time}-{self.end_time})>"


class ClinicHoliday(Base):
    """Specific date holidays/closures (e.g., Christmas, custom days off)."""
    __tablename__ = "clinic_holidays"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True)  # The specific date of holiday
    name = Column(String(255), nullable=False)  # e.g., "Christmas Day", "Staff Training"
    is_full_day = Column(Boolean, default=True, nullable=False)  # Full day off
    
    # If not full day off, can specify custom hours for that day
    start_time = Column(Time, nullable=True)  # Custom opening time if not full day off
    end_time = Column(Time, nullable=True)    # Custom closing time if not full day off
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String(255), nullable=True)  # Who added this holiday

    def __repr__(self):
        return f"<ClinicHoliday(date={self.date}, name={self.name})>"
