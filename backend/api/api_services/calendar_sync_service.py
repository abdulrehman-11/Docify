"""
Calendar Sync Service for two-way synchronization between Google Calendar and Database.

Features:
- Sync changes from DB to Calendar (when appointments are created/updated/deleted)
- Sync changes from Calendar to DB (when events are modified in Calendar)
- Webhook endpoint for real-time Calendar updates (requires public HTTPS)
- Polling-based sync as fallback for development
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any
import logging

# Add agent-python to path
backend_dir = Path(__file__).parent.parent.parent
agent_python_dir = backend_dir / "agent-python"
sys.path.insert(0, str(agent_python_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.appointment import Appointment, AppointmentStatus
from models.patient import Patient

try:
    from services.google_calendar_service import get_calendar_service, CLINIC_TIMEZONE
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    get_calendar_service = None
    CLINIC_TIMEZONE = "Asia/Karachi"

logger = logging.getLogger(__name__)


class CalendarSyncService:
    """Service for two-way Calendar <-> Database synchronization."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.calendar_service = None
        if CALENDAR_AVAILABLE:
            self.calendar_service = get_calendar_service()
            # Initialize if not already done
            if not self.calendar_service._initialized:
                self.calendar_service.initialize()
        
    def _is_available(self) -> bool:
        """Check if calendar service is available."""
        if not self.calendar_service:
            return False
        return self.calendar_service._initialized and self.calendar_service.service is not None
    
    async def sync_calendar_to_db(self) -> Dict[str, Any]:
        """
        Sync changes from Google Calendar back to database.
        
        This handles:
        - Event time changes (reschedule)
        - Event deletions (cancel)
        
        Returns summary of changes made.
        """
        if not self._is_available():
            return {"error": "Calendar service not available"}
        
        results = {
            "updated": 0,
            "cancelled": 0,
            "errors": [],
            "details": []
        }
        
        try:
            # Get all calendar events
            events = self.calendar_service.service.events().list(
                calendarId=self.calendar_service.calendar_id,
                timeMin=datetime.now(timezone.utc).isoformat(),
                maxResults=250,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            calendar_events = {e['id']: e for e in events.get('items', [])}
            
            # Get all DB appointments with calendar event IDs
            stmt = select(Appointment).where(
                Appointment.google_calendar_event_id.isnot(None),
                Appointment.status == AppointmentStatus.CONFIRMED
            )
            db_result = await self.session.execute(stmt)
            appointments = db_result.scalars().all()
            
            for apt in appointments:
                event_id = apt.google_calendar_event_id
                
                if event_id not in calendar_events:
                    # Event was deleted from calendar - cancel in DB
                    apt.status = AppointmentStatus.CANCELLED
                    apt.cancellation_reason = "Cancelled from Google Calendar"
                    results["cancelled"] += 1
                    results["details"].append({
                        "action": "cancelled",
                        "appointment_id": apt.id,
                        "reason": "Event deleted from calendar"
                    })
                    logger.info(f"Cancelled appointment {apt.id} - event deleted from calendar")
                else:
                    # Check if time changed
                    event = calendar_events[event_id]
                    event_start = self._parse_calendar_datetime(event['start'])
                    event_end = self._parse_calendar_datetime(event['end'])
                    
                    # Compare times (strip timezone for comparison since we use wall clock time)
                    db_start = apt.start_time.replace(tzinfo=None)
                    db_end = apt.end_time.replace(tzinfo=None)
                    cal_start = event_start.replace(tzinfo=None)
                    cal_end = event_end.replace(tzinfo=None)
                    
                    if db_start != cal_start or db_end != cal_end:
                        # Time changed in calendar - update DB
                        old_start = apt.start_time
                        apt.start_time = event_start.replace(tzinfo=timezone.utc)
                        apt.end_time = event_end.replace(tzinfo=timezone.utc)
                        results["updated"] += 1
                        results["details"].append({
                            "action": "rescheduled",
                            "appointment_id": apt.id,
                            "old_time": str(old_start),
                            "new_time": str(apt.start_time)
                        })
                        logger.info(f"Updated appointment {apt.id} time from calendar")
            
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Calendar sync error: {e}")
            results["errors"].append(str(e))
            await self.session.rollback()
        
        return results
    
    def _parse_calendar_datetime(self, dt_obj: Dict) -> datetime:
        """Parse datetime from Google Calendar event."""
        if 'dateTime' in dt_obj:
            dt_str = dt_obj['dateTime']
            # Parse ISO format
            if '+' in dt_str or 'Z' in dt_str:
                # Has timezone - parse and convert
                from dateutil import parser
                dt = parser.parse(dt_str)
                return dt
            else:
                # Naive datetime
                return datetime.fromisoformat(dt_str)
        elif 'date' in dt_obj:
            # All-day event
            return datetime.strptime(dt_obj['date'], '%Y-%m-%d')
        else:
            raise ValueError(f"Invalid datetime object: {dt_obj}")
    
    async def get_calendar_changes_since(self, since: datetime) -> List[Dict]:
        """
        Get list of calendar events that changed since a given time.
        Uses incremental sync token if available.
        """
        if not self._is_available():
            return []
        
        try:
            events = self.calendar_service.service.events().list(
                calendarId=self.calendar_service.calendar_id,
                updatedMin=since.isoformat(),
                maxResults=250,
                singleEvents=True
            ).execute()
            
            return events.get('items', [])
        except Exception as e:
            logger.error(f"Error getting calendar changes: {e}")
            return []
    
    async def setup_calendar_watch(self, webhook_url: str) -> Dict:
        """
        Set up push notifications from Google Calendar.
        
        This requires:
        1. A publicly accessible HTTPS endpoint
        2. Domain verification in Google Search Console
        
        Args:
            webhook_url: Public HTTPS URL that Google will call
            
        Returns:
            Watch resource or error
        """
        if not self._is_available():
            return {"error": "Calendar service not available"}
        
        try:
            import uuid
            channel_id = str(uuid.uuid4())
            
            watch_request = {
                'id': channel_id,
                'type': 'web_hook',
                'address': webhook_url,
                'params': {
                    'ttl': '604800'  # 7 days in seconds
                }
            }
            
            response = self.calendar_service.service.events().watch(
                calendarId=self.calendar_service.calendar_id,
                body=watch_request
            ).execute()
            
            logger.info(f"Calendar watch set up: {response}")
            return {
                "success": True,
                "channel_id": channel_id,
                "resource_id": response.get('resourceId'),
                "expiration": response.get('expiration')
            }
            
        except Exception as e:
            logger.error(f"Failed to set up calendar watch: {e}")
            return {"error": str(e)}
    
    async def stop_calendar_watch(self, channel_id: str, resource_id: str) -> Dict:
        """Stop receiving push notifications."""
        if not self._is_available():
            return {"error": "Calendar service not available"}
        
        try:
            self.calendar_service.service.channels().stop(body={
                'id': channel_id,
                'resourceId': resource_id
            }).execute()
            
            return {"success": True}
        except Exception as e:
            logger.error(f"Failed to stop calendar watch: {e}")
            return {"error": str(e)}


# Route handlers for calendar sync
from fastapi import APIRouter, Depends, Request, HTTPException, Header, BackgroundTasks
from api_database import get_db

calendar_router = APIRouter(prefix="/calendar", tags=["Calendar Sync"])


@calendar_router.post("/sync")
async def trigger_calendar_sync(
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger a sync from Google Calendar to database.
    
    Use this to pull changes made in Google Calendar back to the database.
    """
    service = CalendarSyncService(db)
    result = await service.sync_calendar_to_db()
    return result


@calendar_router.post("/webhook")
async def calendar_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_goog_channel_id: Optional[str] = Header(None),
    x_goog_resource_id: Optional[str] = Header(None),
    x_goog_resource_state: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint for Google Calendar push notifications.
    
    Google will call this endpoint when calendar events change.
    Requires public HTTPS URL and domain verification.
    """
    logger.info(f"Calendar webhook received: state={x_goog_resource_state}")
    
    # Google sends a sync message first to verify the webhook
    if x_goog_resource_state == "sync":
        return {"status": "ok", "message": "Webhook verified"}
    
    # For actual changes, sync in background
    if x_goog_resource_state == "exists":
        # Schedule sync in background to respond quickly
        async def do_sync():
            async for session in get_db():
                service = CalendarSyncService(session)
                await service.sync_calendar_to_db()
        
        background_tasks.add_task(do_sync)
    
    return {"status": "ok"}


@calendar_router.post("/setup-watch")
async def setup_calendar_watch(
    webhook_url: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Set up push notifications from Google Calendar.
    
    Requires a publicly accessible HTTPS URL.
    For deployed API: https://docify-839r.onrender.com/calendar/webhook
    """
    service = CalendarSyncService(db)
    result = await service.setup_calendar_watch(webhook_url)
    return result


@calendar_router.get("/status")
async def get_calendar_status():
    """Check calendar integration status."""
    if not CALENDAR_AVAILABLE:
        return {"status": "unavailable", "reason": "Calendar service not imported"}
    
    calendar_service = get_calendar_service()
    if not calendar_service._initialized:
        calendar_service.initialize()
    
    if not calendar_service._initialized or not calendar_service.service:
        return {"status": "unavailable", "reason": "Calendar service not initialized"}
    
    return {
        "status": "available",
        "calendar_id": calendar_service.calendar_id,
        "timezone": CLINIC_TIMEZONE
    }
