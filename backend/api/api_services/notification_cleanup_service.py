"""
Notification Cleanup Service - Automatically delete old notifications
"""
import asyncio
import logging
from datetime import datetime
from api_database import AsyncSessionLocal
from api_services.notification_service import NotificationService

logger = logging.getLogger(__name__)

# Cleanup configuration
CLEANUP_INTERVAL_SECONDS = 86400  # Run once per day (24 hours)
NOTIFICATION_RETENTION_DAYS = 14  # Keep notifications for 14 days

_cleanup_task = None


async def run_notification_cleanup():
    """Run the notification cleanup task once."""
    try:
        async with AsyncSessionLocal() as session:
            service = NotificationService(session)
            deleted_count = await service.cleanup_old_notifications(days=NOTIFICATION_RETENTION_DAYS)
            logger.info(f"🗑️ [Notification Cleanup] Deleted {deleted_count} old notifications")
    except Exception as e:
        logger.error(f"[Notification Cleanup] Error during cleanup: {e}")


async def notification_cleanup_loop():
    """Background task that runs notification cleanup periodically."""
    logger.info(f"🗑️ [Notification Cleanup] Started with interval of {CLEANUP_INTERVAL_SECONDS} seconds ({CLEANUP_INTERVAL_SECONDS // 3600}h)")
    
    while True:
        try:
            logger.info(f"[Notification Cleanup] Running cleanup at {datetime.now()}")
            await run_notification_cleanup()
            logger.info(f"[Notification Cleanup] Cleanup completed, next run in {CLEANUP_INTERVAL_SECONDS // 3600}h")
            
        except asyncio.CancelledError:
            logger.info("[Notification Cleanup] Task cancelled")
            break
        except Exception as e:
            logger.error(f"[Notification Cleanup] Unexpected error: {e}")
        
        # Wait for next interval
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)


async def start_notification_cleanup():
    """Start the background notification cleanup task."""
    global _cleanup_task
    
    if _cleanup_task is not None:
        logger.warning("[Notification Cleanup] Task already running")
        return
    
    logger.info("[Notification Cleanup] Task created")
    
    # Run cleanup immediately on startup
    await run_notification_cleanup()
    
    # Start background loop
    _cleanup_task = asyncio.create_task(notification_cleanup_loop())


async def stop_notification_cleanup():
    """Stop the background notification cleanup task."""
    global _cleanup_task
    
    if _cleanup_task is None:
        return
    
    logger.info("[Notification Cleanup] Stopping...")
    _cleanup_task.cancel()
    
    try:
        await _cleanup_task
    except asyncio.CancelledError:
        pass
    
    _cleanup_task = None
    logger.info("[Notification Cleanup] Stopped")
