"""
Notification API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api_database import get_db
from api_schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse
)
from api_services.notification_service import NotificationService
from typing import Optional

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    user_role: Optional[str] = Query(None, description="Filter by user role (admin/staff)"),
    staff_id: Optional[int] = Query(None, description="Filter by staff ID"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get notifications with optional filters"""
    service = NotificationService(db)
    
    notifications, total, unread_count = await service.get_notifications(
        user_role=user_role,
        staff_id=staff_id,
        is_read=is_read,
        notification_type=notification_type,
        skip=skip,
        limit=limit
    )
    
    return NotificationListResponse(
        notifications=[NotificationResponse.from_orm(n) for n in notifications],
        total=total,
        unread_count=unread_count
    )


@router.post("", response_model=NotificationResponse, status_code=201)
async def create_notification(
    notification: NotificationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new notification (admin use)"""
    service = NotificationService(db)
    created = await service.create_notification(notification)
    return NotificationResponse.from_orm(created)


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    update_data: NotificationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update notification (mark as read/unread)"""
    service = NotificationService(db)
    
    if update_data.is_read:
        notification = await service.mark_as_read(notification_id)
    else:
        raise HTTPException(status_code=400, detail="Only marking as read is supported")
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return NotificationResponse.from_orm(notification)


@router.post("/mark-all-read")
async def mark_all_as_read(
    user_role: Optional[str] = Query(None),
    staff_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read for a user/role"""
    service = NotificationService(db)
    count = await service.mark_all_as_read(user_role=user_role, staff_id=staff_id)
    return {"marked_read": count}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification"""
    service = NotificationService(db)
    success = await service.delete_notification(notification_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification deleted successfully"}


@router.get("/unread-count")
async def get_unread_count(
    user_role: Optional[str] = Query(None),
    staff_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications"""
    service = NotificationService(db)
    _, _, unread_count = await service.get_notifications(
        user_role=user_role,
        staff_id=staff_id,
        is_read=False,
        limit=0
    )
    
    return {"unread_count": unread_count}
