"""Test creating appointment via API"""
import requests
import json
from datetime import datetime, timedelta, timezone

API_BASE = "http://localhost:8000"

# Get a patient first
print("=" * 80)
print("FETCHING PATIENTS")
print("=" * 80)
response = requests.get(f"{API_BASE}/patients")
patients_data = response.json()
print(f"Found {patients_data['total']} patients")

if patients_data['total'] == 0:
    print("No patients available to test with!")
    exit(1)

patient = patients_data['patients'][0]
print(f"\nUsing patient: {patient['name']} (ID: {patient['id']})")

# Try to create an appointment
print("\n" + "=" * 80)
print("CREATING APPOINTMENT")
print("=" * 80)

# Create a time in the future (local time)
now = datetime.now()
start_local = now + timedelta(days=1)
start_local = start_local.replace(hour=14, minute=0, second=0, microsecond=0)
end_local = start_local + timedelta(hours=1)

print(f"\n📍 Local time now: {now}")
print(f"📍 Local timezone offset: {now.astimezone().utcoffset()}")

# Convert to UTC for API
start_utc = start_local.astimezone(timezone.utc)
end_utc = end_local.astimezone(timezone.utc)

print(f"\n📅 Appointment start (local): {start_local}")
print(f"🌍 Appointment start (UTC): {start_utc}")
print(f"📅 Appointment end (local): {end_local}")
print(f"🌍 Appointment end (UTC): {end_utc}")

appointment_data = {
    "patient_id": patient['id'],
    "start_time": start_utc.isoformat(),
    "end_time": end_utc.isoformat(),
    "reason": "Test appointment creation"
}

print(f"\n📤 Sending to API:")
print(json.dumps(appointment_data, indent=2))

try:
    response = requests.post(
        f"{API_BASE}/appointments",
        json=appointment_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n📨 Response status: {response.status_code}")
    print(f"📨 Response headers: {dict(response.headers)}")
    print(f"📨 Response body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 201:
        print("\n✅ Appointment created successfully!")
    else:
        print(f"\n❌ Failed to create appointment!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Now try with naive datetime (like frontend might send)
print("\n" + "=" * 80)
print("TESTING WITH NAIVE DATETIME (like datetime-local)")
print("=" * 80)

# Simulate what datetime-local input gives us
local_str = start_local.strftime("%Y-%m-%dT%H:%M")
print(f"\n📝 datetime-local value: {local_str}")

# When we parse this, it's treated as local time
naive_dt = datetime.fromisoformat(local_str)
print(f"📍 Parsed as naive datetime: {naive_dt}")
print(f"📍 TZ info: {naive_dt.tzinfo}")

# Convert to ISO string (becomes UTC)
iso_str = naive_dt.isoformat()
print(f"🌍 ISO string: {iso_str}")

appointment_data2 = {
    "patient_id": patient['id'],
    "start_time": iso_str,
    "end_time": (naive_dt + timedelta(hours=1)).isoformat(),
    "reason": "Test with naive datetime"
}

print(f"\n📤 Sending to API:")
print(json.dumps(appointment_data2, indent=2))

try:
    response = requests.post(
        f"{API_BASE}/appointments",
        json=appointment_data2,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n📨 Response status: {response.status_code}")
    print(f"📨 Response body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 201:
        print("\n✅ Appointment created successfully!")
        created = response.json()
        print(f"\n🔍 Created appointment:")
        print(f"   Start time returned: {created['start_time']}")
        print(f"   End time returned: {created['end_time']}")
    else:
        print(f"\n❌ Failed to create appointment!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
