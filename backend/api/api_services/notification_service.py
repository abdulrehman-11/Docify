"""
Notification Service for managing system notifications.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, delete
from sqlalchemy.orm import selectinload
from models.notification import Notification, NotificationType
from api_schemas.notification import NotificationCreate, NotificationUpdate
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification management"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_notification(
        self,
        notification_data: NotificationCreate
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_role=notification_data.user_role,
            staff_id=notification_data.staff_id,
            type=NotificationType[notification_data.type.value],
            title=notification_data.title,
            message=notification_data.message,
            data=notification_data.data or {}
        )
        
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        
        logger.info(f"Created notification: {notification.title} (type: {notification.type})")
        return notification

    async def get_notifications(
        self,
        user_role: Optional[str] = None,
        staff_id: Optional[int] = None,
        is_read: Optional[bool] = None,
        notification_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[list[Notification], int, int]:
        """
        Get notifications with filters
        
        Returns:
            Tuple of (notifications, total_count, unread_count)
        """
        # Build filters
        filters = []
        
        # User/role filtering - show notifications that match role or are global
        if user_role:
            filters.append(
                or_(
                    Notification.user_role == user_role,
                    Notification.user_role.is_(None)
                )
            )
        
        if staff_id:
            filters.append(
                or_(
                    Notification.staff_id == staff_id,
                    Notification.staff_id.is_(None)
                )
            )
        
        if is_read is not None:
            filters.append(Notification.is_read == is_read)
        
        if notification_type:
            filters.append(Notification.type == NotificationType[notification_type])
        
        # Get total count
        count_query = select(func.count(Notification.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get unread count
        unread_filters = filters.copy() if filters else []
        unread_filters.append(Notification.is_read == False)
        
        unread_query = select(func.count(Notification.id)).where(and_(*unread_filters))
        unread_result = await self.session.execute(unread_query)
        unread_count = unread_result.scalar() or 0
        
        # Get paginated notifications
        query = select(Notification)
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        notifications = result.scalars().all()
        
        return list(notifications), total, unread_count

    async def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """Mark a notification as read"""
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.session.execute(stmt)
        notification = result.scalar_one_or_none()
        
        if not notification:
            return None
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(notification)
        
        return notification

    async def mark_all_as_read(
        self,
        user_role: Optional[str] = None,
        staff_id: Optional[int] = None
    ) -> int:
        """Mark all notifications as read for a user/role"""
        from sqlalchemy import update
        
        filters = [Notification.is_read == False]
        
        if user_role:
            filters.append(
                or_(
                    Notification.user_role == user_role,
                    Notification.user_role.is_(None)
                )
            )
        
        if staff_id:
            filters.append(
                or_(
                    Notification.staff_id == staff_id,
                    Notification.staff_id.is_(None)
                )
            )
        
        stmt = (
            update(Notification)
            .where(and_(*filters))
            .values(is_read=True, read_at=datetime.utcnow())
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return result.rowcount

    async def delete_notification(self, notification_id: int) -> bool:
        """Delete a notification"""
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.session.execute(stmt)
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
        
        await self.session.delete(notification)
        await self.session.commit()
        
        return True

    # Helper methods for creating specific notification types
    
    async def create_appointment_notification(
        self,
        notification_type: NotificationType,
        patient_name: str,
        appointment_time: datetime,
        appointment_id: int,
        reason: Optional[str] = None
    ) -> Notification:
        """Create an appointment-related notification"""
        type_messages = {
            NotificationType.APPOINTMENT_CREATED: {
                "title": "New Appointment Booked",
                "message": f"New appointment booked for {patient_name} at {appointment_time.strftime('%I:%M %p on %B %d, %Y')}"
            },
            NotificationType.APPOINTMENT_UPDATED: {
                "title": "Appointment Updated",
                "message": f"Appointment for {patient_name} has been updated"
            },
            NotificationType.APPOINTMENT_CANCELLED: {
                "title": "Appointment Cancelled",
                "message": f"Appointment for {patient_name} at {appointment_time.strftime('%I:%M %p on %B %d, %Y')} has been cancelled"
            },
            NotificationType.APPOINTMENT_RESCHEDULED: {
                "title": "Appointment Rescheduled",
                "message": f"Appointment for {patient_name} has been rescheduled to {appointment_time.strftime('%I:%M %p on %B %d, %Y')}"
            },
            NotificationType.APPOINTMENT_UPCOMING: {
                "title": "Upcoming Appointment",
                "message": f"Appointment with {patient_name} starting in 5 minutes"
            }
        }
        
        msg_data = type_messages.get(notification_type, {
            "title": "Appointment Notification",
            "message": f"Appointment for {patient_name}"
        })
        
        notification_create = NotificationCreate(
            user_role="admin",  # Admins and staff see appointment notifications
            type=notification_type.value,
            title=msg_data["title"],
            message=msg_data["message"],
            data={
                "appointment_id": appointment_id,
                "patient_name": patient_name,
                "appointment_time": appointment_time.isoformat(),
                "reason": reason
            }
        )
        
        return await self.create_notification(notification_create)

    async def cleanup_old_notifications(self, days: int = 14) -> int:
        """
        Delete notifications older than specified days.
        
        Args:
            days: Number of days to keep notifications (default: 14)
            
        Returns:
            Number of notifications deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        delete_query = delete(Notification).where(
            Notification.created_at < cutoff_date
        )
        
        result = await self.session.execute(delete_query)
        await self.session.commit()
        
        deleted_count = result.rowcount
        logger.info(f"Cleaned up {deleted_count} notifications older than {days} days")
        
        return deleted_count

    async def create_clinic_hours_notification(self, updated_days: list[str]) -> Notification:
        """Create a clinic hours update notification"""
        days_str = ", ".join(updated_days)
        
        notification_create = NotificationCreate(
            user_role=None,  # All users can see
            type=NotificationType.CLINIC_HOURS_UPDATED.value,
            title="Clinic Hours Updated",
            message=f"Clinic hours have been updated for: {days_str}",
            data={"updated_days": updated_days}
        )
        
        return await self.create_notification(notification_create)
