"""
Google Calendar Service for Hexaa Clinic.
Integrates with Google Calendar API using service account authentication.

Features:
- Create calendar events for new appointments
- Update events when appointments are rescheduled  
- Delete events when appointments are cancelled
- Send email invitations to patients (read-only for patients)
- Full access for clinic doctor (abdul.dev010@gmail.com)
"""

import os
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

logger = logging.getLogger(__name__)

# Timezone for Pakistan Standard Time
CLINIC_TIMEZONE = "Asia/Karachi"
KARACHI_TZ = pytz.timezone(CLINIC_TIMEZONE)

# Doctor's calendar (organizer with full access)
DOCTOR_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "abdul.dev010@gmail.com")

# Scopes needed for calendar operations
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]


class GoogleCalendarService:
    """
    Service for Google Calendar integration.
    
    Uses service account to manage calendar events.
    Doctor (abdul.dev010@gmail.com) has full access.
    Patients receive read-only calendar invites.
    
    Note: For personal Gmail accounts, the calendar must be shared with
    the service account email address.
    """
    
    def __init__(self):
        self.service = None
        self.calendar_id = DOCTOR_CALENDAR_ID
        self._initialized = False
        
    def _get_credentials(self):
        """Get service account credentials from environment or file."""
        # Try environment variable first (for production)
        credentials_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        
        if credentials_json:
            try:
                credentials_info = json.loads(credentials_json)
                logger.info("Using Google credentials from environment variable")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GOOGLE_SERVICE_ACCOUNT_JSON: {e}")
                raise ValueError("Invalid GOOGLE_SERVICE_ACCOUNT_JSON format")
        else:
            # Try loading from file
            credentials_path = os.getenv(
                "GOOGLE_SERVICE_ACCOUNT_FILE",
                "google_service_account.json"
            )
            
            if not os.path.exists(credentials_path):
                logger.warning(f"Google credentials file not found: {credentials_path}")
                return None
                
            with open(credentials_path, 'r') as f:
                credentials_info = json.load(f)
            logger.info(f"Using Google credentials from file: {credentials_path}")
        
        # Create credentials WITHOUT domain-wide delegation
        # For personal Gmail, the calendar must be shared with the service account
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=SCOPES
        )
        
        return credentials
    
    def initialize(self) -> bool:
        """
        Initialize the Google Calendar service.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if self._initialized:
            return True
            
        try:
            credentials = self._get_credentials()
            
            if credentials is None:
                logger.warning("Google Calendar integration disabled - no credentials")
                return False
            
            self.service = build('calendar', 'v3', credentials=credentials)
            self._initialized = True
            logger.info("Google Calendar service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            return False
    
    def _format_datetime(self, dt: datetime) -> Dict[str, str]:
        """
        Format datetime for Google Calendar API.
        
        For demo purposes: Use the raw time from DB as-is.
        If DB says 12:00, calendar shows 12:00 - no timezone conversion.
        """
        # Strip timezone info and use the raw time value
        # DB: 2025-11-26 12:00:00+00:00 -> Calendar shows 12:00
        naive_dt = dt.replace(tzinfo=None)
        
        # Format as ISO string with Karachi timezone
        # This tells Google Calendar to display this exact time in Karachi
        iso_string = naive_dt.isoformat()
        
        return {
            'dateTime': iso_string,
            'timeZone': CLINIC_TIMEZONE
        }
    
    def create_event(
        self,
        patient_name: str,
        patient_email: str,
        patient_phone: str,
        reason: str,
        start_time: datetime,
        end_time: datetime,
        appointment_id: int
    ) -> Optional[str]:
        """
        Create a calendar event for a new appointment.
        
        Args:
            patient_name: Name of the patient
            patient_email: Patient's email (will receive invite)
            patient_phone: Patient's phone number
            reason: Reason for the appointment
            start_time: Appointment start time
            end_time: Appointment end time
            appointment_id: Database appointment ID
            
        Returns:
            Google Calendar event ID if successful, None otherwise
        """
        if not self.initialize():
            logger.warning("Calendar not initialized - skipping event creation")
            return None
            
        try:
            # Format event description with appointment details
            description = (
                f"🏥 Hexaa Clinic Appointment\n\n"
                f"📋 Patient: {patient_name}\n"
                f"📧 Email: {patient_email}\n"
                f"📱 Phone: {patient_phone}\n"
                f"🔖 Reason: {reason}\n\n"
                f"🆔 Appointment ID: {appointment_id}\n\n"
                f"---\n"
                f"⚠️ To reschedule or cancel, please call the clinic.\n"
                f"Patients cannot modify this appointment directly."
            )
            
            event = {
                'summary': f"Hexaa Clinic - {patient_name}",
                'description': description,
                'start': self._format_datetime(start_time),
                'end': self._format_datetime(end_time),
                # Note: Attendees removed for personal Gmail accounts
                # Service accounts can't invite attendees without Domain-Wide Delegation
                # Patient email is included in the description instead
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60},      # 1 hour before
                        {'method': 'popup', 'minutes': 30},      # 30 min before
                    ],
                },
                # Set visibility
                'visibility': 'default',
                # Add color (blue for confirmed)
                'colorId': '1',  # Lavender/Blue
                # Location
                'location': 'Hexaa Clinic, 123 Clinic Way, Suite 200, Springfield',
            }
            
            # Insert event (without sending updates since no attendees)
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                sendUpdates='none'  # No attendees to notify
            ).execute()
            
            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink')
            
            logger.info(
                f"Created calendar event {event_id} for appointment {appointment_id}. "
                f"Link: {event_link}"
            )
            
            return event_id
            
        except HttpError as e:
            logger.error(f"Google Calendar API error creating event: {e}")
            # Log more details for debugging
            if hasattr(e, 'content'):
                logger.error(f"API Error details: {e.content}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating calendar event: {e}")
            return None
    
    def update_event(
        self,
        event_id: str,
        patient_name: str,
        patient_email: str,
        patient_phone: str,
        reason: str,
        start_time: datetime,
        end_time: datetime,
        appointment_id: int
    ) -> bool:
        """
        Update an existing calendar event (for rescheduling).
        
        Args:
            event_id: Google Calendar event ID
            patient_name: Name of the patient
            patient_email: Patient's email
            patient_phone: Patient's phone number
            reason: Reason for the appointment
            start_time: New start time
            end_time: New end time
            appointment_id: Database appointment ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialize():
            logger.warning("Calendar not initialized - skipping event update")
            return False
            
        if not event_id:
            logger.warning("No event_id provided - cannot update event")
            return False
            
        try:
            # Get existing event first
            existing_event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update event details
            description = (
                f"🏥 Hexaa Clinic Appointment (RESCHEDULED)\n\n"
                f"📋 Patient: {patient_name}\n"
                f"📧 Email: {patient_email}\n"
                f"📱 Phone: {patient_phone}\n"
                f"🔖 Reason: {reason}\n\n"
                f"🆔 Appointment ID: {appointment_id}\n"
                f"📅 Rescheduled: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                f"---\n"
                f"⚠️ To reschedule or cancel, please call the clinic.\n"
                f"Patients cannot modify this appointment directly."
            )
            
            existing_event['summary'] = f"Hexaa Clinic - {patient_name}"
            existing_event['description'] = description
            existing_event['start'] = self._format_datetime(start_time)
            existing_event['end'] = self._format_datetime(end_time)
            existing_event['colorId'] = '5'  # Yellow for rescheduled
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=existing_event,
                sendUpdates='none'  # No attendees to notify
            ).execute()
            
            logger.info(f"Updated calendar event {event_id} for appointment {appointment_id}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Calendar event {event_id} not found - may have been deleted")
            else:
                logger.error(f"Google Calendar API error updating event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating calendar event: {e}")
            return False
    
    def delete_event(self, event_id: str, send_notification: bool = True) -> bool:
        """
        Delete a calendar event (for cancellation).
        
        Args:
            event_id: Google Calendar event ID
            send_notification: Whether to send cancellation email
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialize():
            logger.warning("Calendar not initialized - skipping event deletion")
            return False
            
        if not event_id:
            logger.warning("No event_id provided - cannot delete event")
            return False
            
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                sendUpdates='none'  # No attendees to notify
            ).execute()
            
            logger.info(f"Deleted calendar event {event_id}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Calendar event {event_id} not found - already deleted")
                return True  # Consider it success if already gone
            else:
                logger.error(f"Google Calendar API error deleting event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting calendar event: {e}")
            return False
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a calendar event by ID.
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            Event data if found, None otherwise
        """
        if not self.initialize():
            return None
            
        if not event_id:
            return None
            
        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            return event
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Calendar event {event_id} not found")
            else:
                logger.error(f"Google Calendar API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting calendar event: {e}")
            return None
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the calendar connection and return status.
        
        Returns:
            Dictionary with connection status and details
        """
        result = {
            'success': False,
            'message': '',
            'calendar_id': self.calendar_id
        }
        
        if not self.initialize():
            result['message'] = 'Failed to initialize calendar service'
            return result
            
        try:
            # Try to get calendar info
            calendar = self.service.calendars().get(
                calendarId=self.calendar_id
            ).execute()
            
            result['success'] = True
            result['message'] = 'Successfully connected to Google Calendar'
            result['calendar_summary'] = calendar.get('summary', 'Unknown')
            result['calendar_timezone'] = calendar.get('timeZone', 'Unknown')
            
            logger.info(f"Calendar test successful: {calendar.get('summary')}")
            
        except HttpError as e:
            if e.resp.status == 404:
                result['message'] = f'Calendar not found: {self.calendar_id}'
            elif e.resp.status == 403:
                result['message'] = 'Access denied - share calendar with service account'
            else:
                result['message'] = f'API error: {e.reason}'
            logger.error(f"Calendar test failed: {result['message']}")
            
        except Exception as e:
            result['message'] = f'Unexpected error: {str(e)}'
            logger.error(f"Calendar test failed: {e}")
            
        return result


# Singleton instance
_calendar_service: Optional[GoogleCalendarService] = None


def get_calendar_service() -> GoogleCalendarService:
    """Get or create the singleton calendar service instance."""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = GoogleCalendarService()
    return _calendar_service