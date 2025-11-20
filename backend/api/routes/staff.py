"""
Staff management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from api_database import get_db
from api_schemas.staff import (
    StaffCreate,
    StaffUpdate,
    StaffResponse,
    StaffListResponse,
    StaffLogin,
    StaffLoginResponse
)
from api_services.staff_service import StaffService

router = APIRouter()


@router.post("/staff/login", response_model=StaffLoginResponse)
async def staff_login(
    login_data: StaffLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate a staff member"""
    service = StaffService(db)
    
    staff = await service.authenticate_staff(login_data.email, login_data.password)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # In production, generate a proper JWT token
    # For now, using a simple token (you should implement JWT properly)
    token = f"staff_token_{staff.id}"
    
    return StaffLoginResponse(
        access_token=token,
        user=staff
    )


@router.post("/staff", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
async def create_staff(
    staff_data: StaffCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new staff member (admin only)"""
    service = StaffService(db)
    
    try:
        staff = await service.create_staff(
            name=staff_data.name,
            email=staff_data.email,
            password=staff_data.password,
            role=staff_data.role,
            permissions=staff_data.permissions,
            created_by=1  # TODO: Get from authenticated admin
        )
        await db.commit()
        await db.refresh(staff)
        return staff
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/staff", response_model=StaffListResponse)
async def list_staff(
    page: int = 1,
    page_size: int = 50,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all staff members with pagination (admin only)"""
    service = StaffService(db)
    
    skip = (page - 1) * page_size
    staff_list, total = await service.list_staff(
        skip=skip,
        limit=page_size,
        is_active=is_active
    )
    
    return StaffListResponse(
        total=total,
        page=page,
        page_size=page_size,
        staff=staff_list
    )


@router.get("/staff/{staff_id}", response_model=StaffResponse)
async def get_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a staff member by ID"""
    service = StaffService(db)
    
    staff = await service.get_staff_by_id(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    return staff


@router.put("/staff/{staff_id}", response_model=StaffResponse)
async def update_staff(
    staff_id: int,
    staff_data: StaffUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a staff member (admin only)"""
    service = StaffService(db)
    
    try:
        staff = await service.update_staff(
            staff_id=staff_id,
            name=staff_data.name,
            email=staff_data.email,
            password=staff_data.password,
            role=staff_data.role,
            permissions=staff_data.permissions,
            is_active=staff_data.is_active
        )
        await db.commit()
        await db.refresh(staff)
        return staff
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a staff member (soft delete, admin only)"""
    service = StaffService(db)
    
    try:
        await service.delete_staff(staff_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
