"""
Clinic Hours and Dashboard API routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api_database import get_db
from api_schemas.clinic import (
    ClinicHoursResponse,
    ClinicHoursUpdate,
    ClinicHoursCreate,
    DashboardStats,
    TodayAppointment,
    UpcomingAppointment
)
from api_services.clinic_service import ClinicHoursAPIService
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
        hours = await service.update_clinic_hours(
            clinic_hours_id=hours_id,
            start_time=hours_data.start_time,
            end_time=hours_data.end_time,
            is_active=hours_data.is_active
        )
        await db.commit()
        await db.refresh(hours)
        return hours
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


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
            is_active=hours_data.is_active
        )
        await db.commit()
        await db.refresh(hours)
        return hours
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
