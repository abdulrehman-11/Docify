"""Simple test for appointment creation with naive datetime"""
import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

# Get a patient
response = requests.get(f"{API_BASE}/patients")
patients = response.json()['patients']
patient_id = patients[0]['id']

print("Testing appointment creation with naive datetime (like frontend sends)...")
print(f"Using patient ID: {patient_id}")

# Create appointment data with naive datetime (like datetime-local sends)
# This simulates a user selecting 3:00 PM in their local timezone
appointment_data = {
    "patient_id": patient_id,
    "start_time": "2025-11-21T15:00:00",  # Naive datetime
    "end_time": "2025-11-21T16:00:00",    # Naive datetime
    "reason": "Test with naive datetime - should be stored as 3 PM UTC"
}

print(f"\nSending appointment data:")
print(json.dumps(appointment_data, indent=2))

try:
    response = requests.post(
        f"{API_BASE}/appointments",
        json=appointment_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nResponse status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 201:
        print("\n✅ SUCCESS! Appointment created")
        result = response.json()
        print(f"\nStored times:")
        print(f"  Start: {result['start_time']}")
        print(f"  End: {result['end_time']}")
        print(f"\nExpected: Should show 15:00 (3 PM) and 16:00 (4 PM) in UTC")
    else:
        print(f"\n❌ FAILED: {response.json().get('detail')}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
