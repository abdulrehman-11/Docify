"""
Clinic Hours Service for FastAPI.
"""
import sys
from pathlib import Path

# Add agent-python to path
backend_dir = Path(__file__).parent.parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.clinic_hours import ClinicHours, ClinicHoliday
from datetime import time, date
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class ClinicHoursAPIService:
    """Clinic hours service for REST API operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_clinic_hours(self) -> list[ClinicHours]:
        """Get clinic hours for all days."""
        stmt = select(ClinicHours).order_by(ClinicHours.day_of_week)
        result = await self.session.execute(stmt)
        hours = result.scalars().all()
        logger.info(f"Retrieved clinic hours for {len(hours)} days")
        return list(hours)

    async def get_clinic_hours_by_day(self, day_of_week: int) -> Optional[ClinicHours]:
        """Get clinic hours for specific day."""
        stmt = select(ClinicHours).where(ClinicHours.day_of_week == day_of_week)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_clinic_hours(
        self,
        clinic_hours_id: int,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        is_active: Optional[bool] = None,
        break_start: Optional[time] = None,
        break_end: Optional[time] = None,
        clear_break: bool = False
    ) -> ClinicHours:
        """
        Update clinic hours.
        
        Args:
            clinic_hours_id: The ID of the clinic hours record
            start_time: Opening time
            end_time: Closing time
            is_active: Whether clinic is open
            break_start: Break start time
            break_end: Break end time
            clear_break: If True, clear the break times (set to None)
        
        Raises:
            ValueError: If clinic hours not found
        """
        stmt = select(ClinicHours).where(ClinicHours.id == clinic_hours_id)
        result = await self.session.execute(stmt)
        hours = result.scalar_one_or_none()

        if not hours:
            raise ValueError(f"Clinic hours ID {clinic_hours_id} not found")

        if start_time is not None:
            hours.start_time = start_time
        if end_time is not None:
            hours.end_time = end_time
        if is_active is not None:
            hours.is_active = is_active
        
        # Handle break times
        if clear_break:
            hours.break_start = None
            hours.break_end = None
        else:
            if break_start is not None:
                hours.break_start = break_start
            if break_end is not None:
                hours.break_end = break_end

        await self.session.flush()
        logger.info(f"Updated clinic hours ID {clinic_hours_id}")
        return hours

    async def bulk_update_clinic_hours(
        self,
        day_of_weeks: List[int],
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        is_active: Optional[bool] = None,
        break_start: Optional[time] = None,
        break_end: Optional[time] = None
    ) -> List[ClinicHours]:
        """
        Bulk update clinic hours for multiple days.
        
        Args:
            day_of_weeks: List of days to update (0=Monday, 6=Sunday)
            start_time: Opening time
            end_time: Closing time
            is_active: Whether clinic is open
            break_start: Break start time
            break_end: Break end time
            
        Returns:
            List of updated clinic hours
        """
        updated_hours = []
        
        for day in day_of_weeks:
            hours = await self.get_clinic_hours_by_day(day)
            if hours:
                if start_time is not None:
                    hours.start_time = start_time
                if end_time is not None:
                    hours.end_time = end_time
                if is_active is not None:
                    hours.is_active = is_active
                if break_start is not None:
                    hours.break_start = break_start
                if break_end is not None:
                    hours.break_end = break_end
                updated_hours.append(hours)
        
        await self.session.flush()
        logger.info(f"Bulk updated clinic hours for {len(updated_hours)} days")
        return updated_hours

    async def create_clinic_hours(
        self,
        day_of_week: int,
        start_time: time,
        end_time: time,
        is_active: bool = True,
        break_start: Optional[time] = None,
        break_end: Optional[time] = None
    ) -> ClinicHours:
        """
        Create clinic hours for a day.
        
        Raises:
            ValueError: If hours already exist for this day
        """
        # Check if already exists
        existing = await self.get_clinic_hours_by_day(day_of_week)
        if existing:
            raise ValueError(f"Clinic hours already exist for day {day_of_week}")

        hours = ClinicHours(
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            is_active=is_active,
            break_start=break_start,
            break_end=break_end
        )
        self.session.add(hours)
        await self.session.flush()
        logger.info(f"Created clinic hours for day {day_of_week}")
        return hours


class ClinicHolidayAPIService:
    """Clinic holidays service for REST API operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_holidays(self) -> List[ClinicHoliday]:
        """Get all clinic holidays ordered by date."""
        stmt = select(ClinicHoliday).order_by(ClinicHoliday.date)
        result = await self.session.execute(stmt)
        holidays = result.scalars().all()
        logger.info(f"Retrieved {len(holidays)} clinic holidays")
        return list(holidays)

    async def get_upcoming_holidays(self, from_date: Optional[date] = None) -> List[ClinicHoliday]:
        """Get upcoming holidays from a date (defaults to today)."""
        if from_date is None:
            from_date = date.today()
        
        stmt = select(ClinicHoliday).where(
            ClinicHoliday.date >= from_date
        ).order_by(ClinicHoliday.date)
        result = await self.session.execute(stmt)
        holidays = result.scalars().all()
        return list(holidays)

    async def get_holiday_by_id(self, holiday_id: int) -> Optional[ClinicHoliday]:
        """Get a specific holiday by ID."""
        stmt = select(ClinicHoliday).where(ClinicHoliday.id == holiday_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_holiday_by_date(self, holiday_date: date) -> Optional[ClinicHoliday]:
        """Get holiday for a specific date."""
        stmt = select(ClinicHoliday).where(ClinicHoliday.date == holiday_date)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_holiday(
        self,
        holiday_date: date,
        name: str,
        is_full_day: bool = True,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        created_by: Optional[str] = None
    ) -> ClinicHoliday:
        """
        Create a new clinic holiday.
        
        Raises:
            ValueError: If holiday already exists for this date
        """
        existing = await self.get_holiday_by_date(holiday_date)
        if existing:
            raise ValueError(f"Holiday already exists for date {holiday_date}")

        holiday = ClinicHoliday(
            date=holiday_date,
            name=name,
            is_full_day=is_full_day,
            start_time=start_time,
            end_time=end_time,
            created_by=created_by
        )
        self.session.add(holiday)
        await self.session.flush()
        logger.info(f"Created holiday '{name}' for {holiday_date}")
        return holiday

    async def update_holiday(
        self,
        holiday_id: int,
        holiday_date: Optional[date] = None,
        name: Optional[str] = None,
        is_full_day: Optional[bool] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None
    ) -> ClinicHoliday:
        """
        Update a clinic holiday.
        
        Raises:
            ValueError: If holiday not found or date conflict
        """
        holiday = await self.get_holiday_by_id(holiday_id)
        if not holiday:
            raise ValueError(f"Holiday ID {holiday_id} not found")

        # Check for date conflict if changing date
        if holiday_date is not None and holiday_date != holiday.date:
            existing = await self.get_holiday_by_date(holiday_date)
            if existing:
                raise ValueError(f"Holiday already exists for date {holiday_date}")
            holiday.date = holiday_date

        if name is not None:
            holiday.name = name
        if is_full_day is not None:
            holiday.is_full_day = is_full_day
        if start_time is not None:
            holiday.start_time = start_time
        if end_time is not None:
            holiday.end_time = end_time

        await self.session.flush()
        logger.info(f"Updated holiday ID {holiday_id}")
        return holiday

    async def delete_holiday(self, holiday_id: int) -> bool:
        """
        Delete a clinic holiday.
        
        Returns:
            True if deleted, False if not found
        """
        holiday = await self.get_holiday_by_id(holiday_id)
        if not holiday:
            return False
        
        await self.session.delete(holiday)
        await self.session.flush()
        logger.info(f"Deleted holiday ID {holiday_id}")
        return True
