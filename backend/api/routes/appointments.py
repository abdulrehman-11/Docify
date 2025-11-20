"""
Appointment API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
import sys
from pathlib import Path

# Add agent-python to path for existing services
backend_dir = Path(__file__).parent.parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from api_database import get_db
from api_schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentCancel,
    AppointmentResponse,
    AppointmentListResponse,
    AvailabilityRequest,
    AvailabilityResponse,
    AvailabilitySlot
)
from api_services.appointment_service import AppointmentAPIService
from services.appointment_service import AppointmentService  # Import from agent-python

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("", response_model=AppointmentListResponse)
async def list_appointments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (CONFIRMED, CANCELLED, etc.)"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    start_date: Optional[datetime] = Query(None, description="Filter appointments after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter appointments before this date"),
    db: AsyncSession = Depends(get_db)
):
    """Get all appointments with filters and pagination."""
    service = AppointmentAPIService(db)
    skip = (page - 1) * page_size
    
    appointments, total = await service.get_all_appointments(
        skip=skip,
        limit=page_size,
        status=status,
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return AppointmentListResponse(
        total=total,
        page=page,
        page_size=page_size,
        appointments=appointments
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific appointment by ID."""
    service = AppointmentAPIService(db)
    appointment = await service.get_appointment_by_id(appointment_id)
    
    if not appointment:
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    
    return appointment


@router.post("", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new appointment."""
    service = AppointmentAPIService(db)
    
    try:
        appointment = await service.create_appointment(
            patient_id=appointment_data.patient_id,
            start_time=appointment_data.start_time,
            end_time=appointment_data.end_time,
            reason=appointment_data.reason
        )
        await db.commit()
        await db.refresh(appointment)
        return appointment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an appointment."""
    service = AppointmentAPIService(db)
    
    try:
        appointment = await service.update_appointment(
            appointment_id=appointment_id,
            start_time=appointment_data.start_time,
            end_time=appointment_data.end_time,
            reason=appointment_data.reason,
            status=appointment_data.status.value if appointment_data.status else None,
            cancellation_reason=appointment_data.cancellation_reason
        )
        await db.commit()
        await db.refresh(appointment)
        return appointment
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: int,
    cancel_data: AppointmentCancel,
    db: AsyncSession = Depends(get_db)
):
    """Cancel an appointment."""
    service = AppointmentAPIService(db)
    
    try:
        appointment = await service.cancel_appointment(
            appointment_id=appointment_id,
            cancellation_reason=cancel_data.cancellation_reason
        )
        await db.commit()
        await db.refresh(appointment)
        return appointment
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))


@router.delete("/{appointment_id}", status_code=204)
async def delete_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an appointment (hard delete)."""
    service = AppointmentAPIService(db)
    
    deleted = await service.delete_appointment(appointment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    
    await db.commit()
    return None


@router.post("/availability", response_model=AvailabilityResponse)
async def check_availability(
    request: AvailabilityRequest,
    db: AsyncSession = Depends(get_db)
):
    """Check available appointment slots."""
    # Use the existing AppointmentService from agent-python
    service = AppointmentService(db)
    
    try:
        slots = await service.check_availability(
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return AvailabilityResponse(
            slots=[AvailabilitySlot(start=slot["start"], end=slot["end"]) for slot in slots]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
