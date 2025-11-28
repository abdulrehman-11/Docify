"""
Clinic Hours and Dashboard API routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api_database import get_db
from api_schemas.clinic import (
    ClinicHoursResponse,
    ClinicHoursUpdate,
    ClinicHoursCreate,
    ClinicHoursBulkUpdate,
    ClinicHolidayResponse,
    ClinicHolidayCreate,
    ClinicHolidayUpdate,
    DashboardStats,
    TodayAppointment,
    UpcomingAppointment
)
from api_services.clinic_service import ClinicHoursAPIService, ClinicHolidayAPIService
from api_services.appointment_service import AppointmentAPIService

router = APIRouter(tags=["Clinic & Dashboard"])


# Clinic Hours endpoints
@router.get("/clinic/hours", response_model=list[ClinicHoursResponse])
async def get_clinic_hours(db: AsyncSession = Depends(get_db)):
    """Get clinic hours for all days."""
    service = ClinicHoursAPIService(db)
    hours = await service.get_all_clinic_hours()
    return hours


@router.put("/clinic/hours/{hours_id}", response_model=ClinicHoursResponse)
async def update_clinic_hours(
    hours_id: int,
    hours_data: ClinicHoursUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update clinic hours for a specific day."""
    service = ClinicHoursAPIService(db)
    
    try:
        # Check if we need to clear break times
        # If break_start or break_end is explicitly set to empty string in request, clear them
        hours = await service.update_clinic_hours(
            clinic_hours_id=hours_id,
            start_time=hours_data.start_time,
            end_time=hours_data.end_time,
            is_active=hours_data.is_active,
            break_start=hours_data.break_start,
            break_end=hours_data.break_end
        )
        await db.commit()
        await db.refresh(hours)
        return hours
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/clinic/hours/{hours_id}/clear-break", response_model=ClinicHoursResponse)
async def clear_break_time(
    hours_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Clear break time for a specific day."""
    service = ClinicHoursAPIService(db)
    
    try:
        hours = await service.update_clinic_hours(
            clinic_hours_id=hours_id,
            clear_break=True
        )
        await db.commit()
        await db.refresh(hours)
        return hours
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/clinic/hours/bulk", response_model=List[ClinicHoursResponse])
async def bulk_update_clinic_hours(
    bulk_data: ClinicHoursBulkUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Bulk update clinic hours for multiple days (apply to all selected days)."""
    service = ClinicHoursAPIService(db)
    
    try:
        hours_list = await service.bulk_update_clinic_hours(
            day_of_weeks=bulk_data.day_of_weeks,
            start_time=bulk_data.start_time,
            end_time=bulk_data.end_time,
            is_active=bulk_data.is_active,
            break_start=bulk_data.break_start,
            break_end=bulk_data.break_end
        )
        await db.commit()
        # Refresh all updated records
        for hours in hours_list:
            await db.refresh(hours)
        return hours_list
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/clinic/hours", response_model=ClinicHoursResponse, status_code=201)
async def create_clinic_hours(
    hours_data: ClinicHoursCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create clinic hours for a day."""
    service = ClinicHoursAPIService(db)
    
    try:
        hours = await service.create_clinic_hours(
            day_of_week=hours_data.day_of_week,
            start_time=hours_data.start_time,
            end_time=hours_data.end_time,
            is_active=hours_data.is_active,
            break_start=hours_data.break_start,
            break_end=hours_data.break_end
        )
        await db.commit()
        await db.refresh(hours)
        return hours
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Clinic Holiday endpoints
@router.get("/clinic/holidays", response_model=List[ClinicHolidayResponse])
async def get_clinic_holidays(
    upcoming_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get all clinic holidays. Use upcoming_only=true to get only future holidays."""
    service = ClinicHolidayAPIService(db)
    
    if upcoming_only:
        holidays = await service.get_upcoming_holidays()
    else:
        holidays = await service.get_all_holidays()
    return holidays


@router.get("/clinic/holidays/{holiday_id}", response_model=ClinicHolidayResponse)
async def get_clinic_holiday(
    holiday_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific clinic holiday by ID."""
    service = ClinicHolidayAPIService(db)
    
    holiday = await service.get_holiday_by_id(holiday_id)
    if not holiday:
        raise HTTPException(status_code=404, detail=f"Holiday ID {holiday_id} not found")
    return holiday


@router.post("/clinic/holidays", response_model=ClinicHolidayResponse, status_code=201)
async def create_clinic_holiday(
    holiday_data: ClinicHolidayCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new clinic holiday."""
    service = ClinicHolidayAPIService(db)
    
    try:
        holiday = await service.create_holiday(
            holiday_date=holiday_data.date,
            name=holiday_data.name,
            is_full_day=holiday_data.is_full_day,
            start_time=holiday_data.start_time,
            end_time=holiday_data.end_time
        )
        await db.commit()
        await db.refresh(holiday)
        return holiday
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/clinic/holidays/{holiday_id}", response_model=ClinicHolidayResponse)
async def update_clinic_holiday(
    holiday_id: int,
    holiday_data: ClinicHolidayUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing clinic holiday."""
    service = ClinicHolidayAPIService(db)
    
    try:
        holiday = await service.update_holiday(
            holiday_id=holiday_id,
            holiday_date=holiday_data.date,
            name=holiday_data.name,
            is_full_day=holiday_data.is_full_day,
            start_time=holiday_data.start_time,
            end_time=holiday_data.end_time
        )
        await db.commit()
        await db.refresh(holiday)
        return holiday
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/clinic/holidays/{holiday_id}", status_code=204)
async def delete_clinic_holiday(
    holiday_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a clinic holiday."""
    service = ClinicHolidayAPIService(db)
    
    deleted = await service.delete_holiday(holiday_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Holiday ID {holiday_id} not found")
    
    await db.commit()
    return None


# Dashboard endpoints
@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics."""
    service = AppointmentAPIService(db)
    stats = await service.get_appointment_stats()
    return stats


@router.get("/dashboard/today", response_model=list[TodayAppointment])
async def get_today_appointments(db: AsyncSession = Depends(get_db)):
    """Get today's appointments."""
    service = AppointmentAPIService(db)
    appointments = await service.get_today_appointments()
    return appointments


@router.get("/dashboard/upcoming", response_model=list[UpcomingAppointment])
async def get_upcoming_appointments(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get upcoming appointments for next N days."""
    service = AppointmentAPIService(db)
    appointments = await service.get_upcoming_appointments(days=days)
    return appointments
