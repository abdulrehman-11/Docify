"""
Patient API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from api_database import get_db
from api_schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)
from api_services.patient_service import PatientAPIService

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("", response_model=PatientListResponse)
async def list_patients(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    db: AsyncSession = Depends(get_db)
):
    """Get all patients with pagination and optional search."""
    service = PatientAPIService(db)
    skip = (page - 1) * page_size
    
    patients, total = await service.get_all_patients(
        skip=skip,
        limit=page_size,
        search=search
    )
    
    return PatientListResponse(
        total=total,
        page=page,
        page_size=page_size,
        patients=patients
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific patient by ID."""
    service = PatientAPIService(db)
    patient = await service.get_patient_by_id(patient_id)
    
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    
    return patient


@router.post("", response_model=PatientResponse, status_code=201)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new patient."""
    service = PatientAPIService(db)
    
    try:
        patient = await service.create_patient(
            name=patient_data.name,
            email=patient_data.email,
            phone=patient_data.phone,
            insurance_provider=patient_data.insurance_provider
        )
        await db.commit()
        await db.refresh(patient)
        return patient
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update patient information."""
    service = PatientAPIService(db)
    
    try:
        patient = await service.update_patient(
            patient_id=patient_id,
            name=patient_data.name,
            email=patient_data.email,
            phone=patient_data.phone,
            insurance_provider=patient_data.insurance_provider
        )
        await db.commit()
        await db.refresh(patient)
        return patient
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))


@router.delete("/{patient_id}", status_code=204)
async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a patient (cascade deletes all appointments)."""
    service = PatientAPIService(db)
    
    deleted = await service.delete_patient(patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    
    await db.commit()
    return None
