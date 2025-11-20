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
from sqlalchemy import select
from models.clinic_hours import ClinicHours
from datetime import time
from typing import Optional
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
        is_active: Optional[bool] = None
    ) -> ClinicHours:
        """
        Update clinic hours.
        
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

        await self.session.flush()
        logger.info(f"Updated clinic hours ID {clinic_hours_id}")
        return hours

    async def create_clinic_hours(
        self,
        day_of_week: int,
        start_time: time,
        end_time: time,
        is_active: bool = True
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
            is_active=is_active
        )
        self.session.add(hours)
        await self.session.flush()
        logger.info(f"Created clinic hours for day {day_of_week}")
        return hours
