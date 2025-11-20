# Verification Script for Timezone Fix

## Step 1: Verify Backend is Running
Open a terminal and run:
```bash
curl http://localhost:8000/health
```
Expected output: `{"status":"healthy","service":"ether-clinic-api"}`

## Step 2: Test Appointment Creation
Run this command to create a test appointment:
```bash
curl -X POST http://localhost:8000/appointments \
  -H "Content-Type: application/json" \
  -d "{\"patient_id\": 9, \"start_time\": \"2025-11-23T15:00:00\", \"end_time\": \"2025-11-23T16:00:00\", \"reason\": \"Verification test\"}"
```

Expected: Status 201 with response showing `start_time: "2025-11-23T15:00:00+00:00"`

## Step 3: Verify Existing Appointments
```bash
curl "http://localhost:8000/appointments?page_size=3"
```

Check that times are displayed with `+00:00` timezone indicator.

## Step 4: Start Frontend (if not running)
```bash
cd frontend
npm run dev
```

## Step 5: Test in Browser
1. Open http://localhost:5173 (or whatever port your frontend uses)
2. Navigate to Appointments page
3. Click "New Appointment"
4. Select:
   - Patient: Any patient
   - Start Time: Tomorrow at 2:00 PM
   - End Time: Tomorrow at 3:00 PM
   - Reason: "Test appointment"
5. Click "Create Appointment"

**Expected Results:**
- ✅ Appointment should be created successfully
- ✅ The displayed time should be 2:00 PM (not 7:00 PM or 9:00 AM)
- ✅ No error about time slot conflicts

## Step 6: Verify Display
1. Find the appointment you just created in the list
2. Verify the time shows as "2:00 PM" (or whatever time you selected)
3. The time should NOT be shifted by 5 hours

## Troubleshooting

### If appointment creation fails:
1. Check browser console for errors
2. Check backend terminal for logs
3. Verify patient ID exists in the database

### If times still show incorrectly:
1. Clear browser cache and reload (Ctrl+Shift+R)
2. Restart the frontend dev server
3. Check that all files were saved properly

## All Tests Passing?
If all tests pass, your timezone and appointment creation issues are resolved! ✅

---

**Note:** The backend changes are already in effect. Frontend changes require a browser refresh if the dev server was already running.
