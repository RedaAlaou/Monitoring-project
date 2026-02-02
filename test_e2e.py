import requests
import time
import json

# URLs
AUTH_URL = "http://localhost:8000/api/v1/users" # Check if /api/v1 is needed
DEVICE_URL = "http://localhost:8001/api/v1/devices"
MONITORING_URL = "http://localhost:8002/api/v1/telemetry"

# Test Data
USER_EMAIL = f"test_{int(time.time())}@example.com"
USER_PASS = "password123"
DEVICE_SERIAL = f"SN-{int(time.time())}"

def test_e2e():
    print("--- Starting End-to-End Test ---")
    
    # 1. Register User
    print(f"\n1. Registering user: {USER_EMAIL}")
    # Note: Checking backend-api-v1/main.py for prefix. 
    # auth_controller has prefix="/users". main.py includes it.
    reg_resp = requests.post(f"http://localhost:8000/users/add", 
                            json={"email": USER_EMAIL, "password": USER_PASS})
    if reg_resp.status_code != 200:
        print(f"Failed to register: {reg_resp.text}")
        return
    print("User registered successfully")

    # 2. Login
    print("\n2. Logging in...")
    login_resp = requests.post(f"http://localhost:8000/users/auth", 
                              json={"email": USER_EMAIL, "password": USER_PASS})
    if login_resp.status_code != 200:
        print(f"Failed to login: {login_resp.text}")
        return
    token = login_resp.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful, token retrieved")

    # 3. Add Device
    print(f"\n3. Adding device: {DEVICE_SERIAL}")
    device_data = {
        "name": "E2E Test Sensor",
        "type": "sensor",
        "serial_number": DEVICE_SERIAL,
        "description": "Device created during E2E test",
        "location": "Warehouse 1"
    }
    dev_resp = requests.post(DEVICE_URL + "/", json=device_data, headers=headers)
    if dev_resp.status_code != 201:
        print(f"Failed to add device: {dev_resp.text}")
        return
    device_id = dev_resp.json().get("id")
    print(f"Device added with ID: {device_id}")

    # 4. Reserve Device
    print(f"\n4. Reserving device {device_id}...")
    res_resp = requests.put(f"{DEVICE_URL}/{device_id}/reserve", 
                           json={"notes": "Reserved for test order"}, headers=headers)
    if res_resp.status_code != 200:
        print(f"Failed to reserve device: {res_resp.text}")
        return
    print("Device reserved successfully")

    # 5. Deploy Device
    print(f"\n5. Deploying device {device_id}...")
    dep_resp = requests.put(f"{DEVICE_URL}/{device_id}/deploy", 
                           json={"location": "Field Office A", "notes": "Moving to the field"}, headers=headers)
    if dep_resp.status_code != 200:
        print(f"Failed to deploy device: {dep_resp.text}")
        return
    print("Device deployed successfully")

    # 6. Send Telemetry
    print(f"\n6. Sending telemetry for device {device_id}...")
    telemetry_data = {
        "device_id": device_id,
        "device_name": "E2E Test Sensor",
        "timestamp": "2026-02-01T12:00:00Z",
        "location": "Field Office A",
        "temperature": 22.5,
        "humidity": 45.0
    }
    # Using the new endpoint we added
    tel_resp = requests.post(f"{DEVICE_URL}/telemetry", json=telemetry_data, headers=headers)
    if tel_resp.status_code != 200:
        print(f"Failed to send telemetry: {tel_resp.text}")
        return
    print("Telemetry sent successfully")

    # 7. Verify in Monitoring
    print("\n7. Verifying telemetry in Monitoring service...")
    time.sleep(2) # Wait for RabbitMQ to process
    mon_resp = requests.get(f"{MONITORING_URL}/?device_id={device_id}")
    if mon_resp.status_code != 200:
        print(f"Failed to get monitoring data: {mon_resp.text}")
        return
    
    data = mon_resp.json()
    if len(data) > 0:
        print("Telemetry found in Monitoring DB!")
        print(json.dumps(data[0], indent=2))
    else:
        print("Telemetry not found in Monitoring DB yet. Check RabbitMQ and Consumer logs.")

    print("\n--- E2E Test Completed ---")

if __name__ == "__main__":
    try:
        test_e2e()
    except Exception as e:
        print(f"Test error: {e}")
