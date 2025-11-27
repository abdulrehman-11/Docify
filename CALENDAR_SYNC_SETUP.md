# Google Calendar Bi-Directional Sync Setup Guide

This guide explains how to set up and use the bi-directional calendar synchronization between your Neon PostgreSQL database and Google Calendar.

## Overview

The system now supports:
1. **DB → Calendar**: When appointments are created via Frontend or Voice Agent, they appear in Google Calendar
2. **Calendar → DB**: When appointments are modified in Google Calendar, changes sync back to the database
3. **Bi-directional**: Full sync in both directions

## Prerequisites

### 1. Google Service Account Setup
You already have a service account: `hexaa-clinic-calendar-service@hexaa-clinic-calendar.iam.gserviceaccount.com`

### 2. Calendar Sharing (CRITICAL!)
The Google Calendar must be shared with the service account:

1. Open Google Calendar (https://calendar.google.com)
2. Find the calendar (abdul.dev010@gmail.com) in the left sidebar
3. Click the three dots → "Settings and sharing"
4. Scroll to "Share with specific people or groups"
5. Add: `hexaa-clinic-calendar-service@hexaa-clinic-calendar.iam.gserviceaccount.com`
6. Set permission to: **"Make changes to events"**
7. Click "Send"

## Render Deployment Configuration

### Environment Variables to Add in Render Dashboard:

1. Go to: https://dashboard.render.com → Your ether-clinic-api service → Environment

2. Add these environment variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your Neon PostgreSQL connection string |
| `ALLOWED_ORIGINS` | Your frontend URLs (comma-separated) |
| `GOOGLE_CALENDAR_ID` | `abdul.dev010@gmail.com` |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | (Paste entire JSON content - see below) |

### GOOGLE_SERVICE_ACCOUNT_JSON Value:
Copy-paste the entire content of your Google Service Account JSON file (the one you downloaded from Google Cloud Console). It should look like this:

```
{"type":"service_account","project_id":"your-project-id","private_key_id":"xxx","private_key":"-----BEGIN PRIVATE KEY-----\n...<YOUR_PRIVATE_KEY>...\n-----END PRIVATE KEY-----\n","client_email":"your-service-account@your-project.iam.gserviceaccount.com","client_id":"123456789","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/...","universe_domain":"googleapis.com"}
```

**Important:** Paste the ENTIRE content of your service account JSON file as one continuous string.

## Auto-Sync Feature (NEW!)

The API now includes **automatic background synchronization** that runs every 5 minutes by default. This means:

- ✅ Changes made in Google Calendar are **automatically** synced to the database
- ✅ No need to call `/calendar/sync` manually
- ✅ Starts automatically when the API server starts

### Configuration (Optional)

Add these environment variables in Render to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTO_SYNC_ENABLED` | `true` | Set to `false` to disable auto-sync |
| `AUTO_SYNC_INTERVAL` | `300` | Sync interval in seconds (300 = 5 minutes) |

### Auto-Sync Endpoints

```bash
# Check auto-sync status
GET https://docify-839r.onrender.com/calendar/auto-sync/status

# Manually start auto-sync (if stopped)
POST https://docify-839r.onrender.com/calendar/auto-sync/start

# Stop auto-sync
POST https://docify-839r.onrender.com/calendar/auto-sync/stop
```

## API Endpoints

After deployment, these calendar sync endpoints are available:

### Check Status
```bash
GET https://docify-839r.onrender.com/calendar/status
```
Should return:
```json
{
  "status": "available",
  "calendar_id": "abdul.dev010@gmail.com",
  "timezone": "Asia/Karachi",
  "auto_sync": {
    "enabled": true,
    "running": true,
    "interval_seconds": 300,
    "last_sync_time": "2025-11-27T10:00:00Z",
    "last_sync_result": {"updated": 0, "cancelled": 0}
  }
}
```

### Sync DB → Calendar (Create missing calendar events)
```bash
POST https://docify-839r.onrender.com/calendar/sync-to-calendar
```
This creates Google Calendar events for all appointments that don't have them.

### Sync Calendar → DB (Pull changes from calendar)
```bash
POST https://docify-839r.onrender.com/calendar/sync
```
This updates the database when appointments are modified or deleted in Google Calendar.

### Full Bi-directional Sync
```bash
POST https://docify-839r.onrender.com/calendar/full-sync
```
Runs both syncs: first DB→Calendar, then Calendar→DB.

### View Calendar Events
```bash
GET https://docify-839r.onrender.com/calendar/events
```
Lists all upcoming events in Google Calendar.

## Initial Setup After Deployment

1. **First, redeploy on Render** to pick up the new code
2. **Add the environment variables** in Render dashboard
3. **Test calendar status**: `GET /calendar/status`
4. **Sync existing appointments to calendar**: `POST /calendar/sync-to-calendar`
5. **Verify events appear in Google Calendar**

## How It Works

### When Creating Appointments (Automatic)
- Frontend creates appointment via `/appointments` API → Calendar event created automatically
- Voice Agent books appointment → Calendar event created automatically
- DB stores `google_calendar_event_id` for linking

### When Updating Appointments (Automatic)
- Frontend updates appointment → Calendar event updated automatically
- Voice Agent reschedules → Old event deleted, new event created

### When Cancelling Appointments (Automatic)
- Frontend/Voice Agent cancels → Calendar event deleted automatically

### Syncing Calendar Changes to DB (NOW AUTOMATIC!)
- **Auto-sync runs every 5 minutes** - no action needed!
- Or call `POST /calendar/sync` for immediate sync
- Or set up webhook for real-time updates: `POST /calendar/setup-watch`

## Setting Up Real-Time Webhook (Optional)

For automatic sync when calendar is modified:

```bash
POST https://docify-839r.onrender.com/calendar/setup-watch
Content-Type: application/json

{
  "webhook_url": "https://docify-839r.onrender.com/calendar/webhook"
}
```

Note: This requires the Render service to be on a paid plan (not free tier) for reliable webhook delivery.

## Troubleshooting

### "Calendar service not imported"
- Check that `google-api-python-client` is installed
- Verify the build command installs agent-python requirements

### "Calendar service not initialized"
- Check `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable
- Verify the calendar is shared with the service account email

### Events not appearing in calendar
1. Check calendar sharing permissions
2. Run `POST /calendar/sync-to-calendar` to sync existing appointments
3. Check `/calendar/status` returns "available"

### Changes in calendar not reflected in DB
1. Run `POST /calendar/sync` manually
2. Or set up the webhook for real-time sync

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│   FastAPI API   │────▶│  Neon Postgres  │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
┌─────────────────┐              │              ┌─────────────────┐
│   Voice Agent   │──────────────┤              │ Google Calendar │
└─────────────────┘              └─────────────▶└─────────────────┘
                                      ▲
                                      │
                              (bi-directional sync)
```
