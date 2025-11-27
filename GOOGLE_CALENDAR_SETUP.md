# Google Calendar Integration Guide

## Overview

This document describes the Google Calendar integration for Hexaa Clinic's appointment booking system.

### Features
- ✅ **Automatic calendar event creation** when appointments are booked
- ✅ **Event updates** when appointments are rescheduled  
- ✅ **Event deletion** when appointments are cancelled
- ✅ **Email invitations** sent to patients automatically
- ✅ **Doctor's calendar** (abdul.dev010@gmail.com) shows all appointments
- ✅ **Patients receive read-only** calendar invites (cannot modify)

---

## Setup Instructions

### Step 1: Google Cloud Console Setup (Already Done)

You've already:
- Created project: `hexaa-clinic-calendar`
- Enabled Google Calendar API
- Created service account: `hexaa-clinic-calendar-service@hexaa-clinic-calendar.iam.gserviceaccount.com`

### Step 2: Enable Domain-Wide Delegation (REQUIRED)

**⚠️ IMPORTANT**: Service accounts need domain-wide delegation to access user calendars.

Since you're using a personal Gmail (not Google Workspace), you have two options:

#### Option A: Share Calendar with Service Account (Recommended for personal Gmail)

1. Go to https://calendar.google.com
2. Click Settings (gear icon) → Settings
3. On the left, click your calendar (`abdul.dev010@gmail.com`)
4. Scroll to "Share with specific people or groups"
5. Click "+ Add people and groups"
6. Add the service account email:
   ```
   hexaa-clinic-calendar-service@hexaa-clinic-calendar.iam.gserviceaccount.com
   ```
7. Set permission to: **"Make changes to events"**
8. Click "Send"

#### Option B: Use OAuth 2.0 (Alternative)

If Option A doesn't work, you'll need OAuth 2.0 with user consent. Let me know if you need this alternative.

### Step 3: Save Service Account Credentials

1. Copy the service account JSON file to:
   ```
   backend/agent-python/google_service_account.json
   ```

2. The file should look like this:
   ```json
   {
     "type": "service_account",
     "project_id": "hexaa-clinic-calendar",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "hexaa-clinic-calendar-service@hexaa-clinic-calendar.iam.gserviceaccount.com",
     "client_id": "...",
     ...
   }
   ```

### Step 4: Configure Environment Variables

Add to your `.env.local` file:

```bash
# Google Calendar Integration
GOOGLE_SERVICE_ACCOUNT_FILE=google_service_account.json
GOOGLE_CALENDAR_ID=abdul.dev010@gmail.com
```

**For Production (Render/Vercel):**

Set as environment variable using the JSON content directly:

```bash
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"hexaa-clinic-calendar",...}
GOOGLE_CALENDAR_ID=abdul.dev010@gmail.com
```

### Step 5: Install Dependencies

```bash
cd backend/agent-python
pip install -r requirements.txt

cd ../api
pip install -r requirements.txt
```

### Step 6: Run Database Migration

```bash
cd backend/agent-python
alembic upgrade head
```

This adds the `google_calendar_event_id` column to the appointments table.

---

## How It Works

### When Appointment is Booked:

1. Appointment is saved to database
2. Google Calendar event is created on doctor's calendar
3. Patient receives email invitation (read-only access)
4. Event ID is stored in `appointments.google_calendar_event_id`

### When Appointment is Cancelled:

1. Appointment status changed to CANCELLED
2. Calendar event is deleted
3. Patient receives cancellation email notification

### When Appointment is Rescheduled:

1. Old appointment marked as RESCHEDULED
2. New appointment created
3. Calendar event updated with new time
4. Patient receives update email notification

---

## Calendar Event Details

### Event Format:

```
Title: Hexaa Clinic - [Patient Name]

Description:
🏥 Hexaa Clinic Appointment

📋 Patient: John Doe
📧 Email: john@example.com
📱 Phone: +92-300-1234567
🔖 Reason: General Checkup

🆔 Appointment ID: 123

---
⚠️ To reschedule or cancel, please call the clinic.
Patients cannot modify this appointment directly.
```

### Reminders (Automatic):

- 📧 Email: 24 hours before
- 📧 Email: 1 hour before
- 🔔 Popup: 30 minutes before

---

## Permissions

| User | Calendar Access | Can Edit Events |
|------|-----------------|-----------------|
| Doctor (abdul.dev010@gmail.com) | Full access | ✅ Yes |
| Patients | View only | ❌ No |

---

## Troubleshooting

### "Credentials not found" Error

1. Check if `google_service_account.json` exists in `backend/agent-python/`
2. Check environment variable is set correctly

### "Access Denied" Error

1. Ensure calendar is shared with service account
2. Check permission is "Make changes to events"
3. Wait 5 minutes for changes to propagate

### Events Not Appearing in Calendar

1. Check service account has calendar access
2. Verify `GOOGLE_CALENDAR_ID` is correct
3. Check logs for API errors

### Patient Not Receiving Emails

1. Check patient email is valid
2. Check spam folder
3. Verify `sendUpdates: 'all'` in API call

---

## Files Changed

```
backend/agent-python/
├── models/appointment.py         # Added google_calendar_event_id field
├── services/google_calendar_service.py  # NEW - Calendar integration
├── tools/handlers.py             # Updated book/cancel/reschedule handlers
├── requirements.txt              # Added Google API dependencies
├── .env.example                  # Added calendar config
└── alembic/versions/
    └── 003_add_google_calendar_event_id.py  # NEW - Migration

backend/api/
├── api_services/appointment_service.py  # Added calendar sync
├── requirements.txt              # Added Google API dependencies
└── .env.example                  # Added calendar config
```

---

## Testing

### Test 1: Book Appointment

1. Book an appointment through the voice agent or frontend
2. Check doctor's Google Calendar for new event
3. Check patient's email for invitation

### Test 2: Cancel Appointment

1. Cancel an existing appointment
2. Event should disappear from calendar
3. Patient receives cancellation email

### Test 3: Reschedule Appointment

1. Reschedule an appointment
2. Event time should update in calendar
3. Patient receives update email

---

## Production Deployment

### Render

1. Go to Render dashboard
2. Select your backend service
3. Go to "Environment" tab
4. Add:
   - `GOOGLE_SERVICE_ACCOUNT_JSON` = (paste full JSON content)
   - `GOOGLE_CALENDAR_ID` = `abdul.dev010@gmail.com`

### Vercel (if using)

1. Go to project settings
2. Add environment variables same as above

---

## Security Notes

⚠️ **NEVER commit these files to Git:**
- `google_service_account.json`
- `.env.local`
- Any file containing private keys

The `.gitignore` should already include these patterns.
