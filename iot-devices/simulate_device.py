#!/usr/bin/env python3
"""
IoT Device Simulator
Simulates IoT devices sending telemetry data and events to the Device Management service.
Auto-provisions devices if they don't exist in the database.
"""

import asyncio
import random
import requests
import json
import uuid
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DeviceConfig:
    """Configuration for a simulated device."""
    device_id: int # Placeholder, will be updated from DB
    device_name: str
    device_type: str
    base_location: str
    interval_seconds: float
    serial_number: str = "" # Added for identification

    def __post_init__(self):
        if not self.serial_number:
            # Generate a consistent serial based on name to allow restarts to find the same device
            slug = self.device_name.replace(' ', '-').upper()
            self.serial_number = f"SN-{slug}-001"


class IoTSimulator:
    """Simulates multiple IoT devices sending data."""

    def __init__(
        self, 
        api_base_url: str = "http://localhost:8001",
        auth_url: str = "http://localhost:8000/users/auth",
        email: str = "admin@example.com",
        password: str = "admin123"
    ):
        self.api_base_url = api_base_url
        self.auth_url = auth_url
        self.email = email
        self.password = password
        self.token = None
        self.devices: List[DeviceConfig] = []
        self.running = False
        self.loop = None

    def authenticate(self) -> bool:
        """Authenticate with the Signing service to get a JWT token."""
        try:
            print(f"Authenticating as {self.email}...")
            response = requests.post(
                self.auth_url,
                json={"email": self.email, "password": self.password},
                timeout=30
            )
            if response.status_code == 200:
                self.token = response.json().get("token")
                print("✅ Authentication successful")
                return True
            
            # If auth fails, try to register
            if response.status_code == 401:
                print("Authentication failed. Trying to register...")
                if self.register():
                    # Retry auth after registration
                     return self.authenticate_retry()
            
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    def authenticate_retry(self) -> bool:
        """Retry authentication after registration."""
        try:
            response = requests.post(
                self.auth_url,
                json={"email": self.email, "password": self.password},
                timeout=30
            )
            if response.status_code == 200:
                self.token = response.json().get("token")
                print("✅ Authentication successful after registration")
                return True
            return False
        except:
            return False

    def register(self) -> bool:
        """Register the user."""
        try:
            register_url = self.auth_url.replace("/auth", "/add")
            response = requests.post(
                register_url,
                json={"email": self.email, "password": self.password},
                timeout=30
            )
            if response.status_code in [200, 201]:
                print(f"✅ Registration successful for {self.email}")
                return True
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False

    def add_device(self, device: DeviceConfig):
        """Add a device to simulate."""
        self.devices.append(device)

    async def _send_request(self, method, url, **kwargs):
        """Run blocking requests in executor."""
        if not self.loop:
            self.loop = asyncio.get_running_loop()
        
        return await self.loop.run_in_executor(
            None, 
            lambda: requests.request(method, url, **kwargs)
        )

    def provision_devices(self):
        """Synchronously provision devices in the DB before starting async loop."""
        print("\n🔧 Provisioning devices...")
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
             # 1. Get existing devices
            response = requests.get(
                f"{self.api_base_url}/api/v1/devices/?page_size=100", 
                headers=headers,
                timeout=45
            )
            
            existing_devices = []
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "devices" in data:
                    existing_devices = data["devices"]
                elif isinstance(data, list):
                    existing_devices = data
            
            print(f"Found {len(existing_devices)} existing devices in DB.")
            
            for config in self.devices:
                # Find by serial number match
                found = next((d for d in existing_devices if d.get('serial_number') == config.serial_number), None)
                
                if found:
                    config.device_id = found['id']
                    status = found.get('status', '').lower()
                    print(f"  🔹 Device '{config.device_name}' found (ID: {config.device_id}, Status: {status})")
                    
                    if status != 'deployed':
                        print(f"  🚀 Deploying device {config.device_id}...")
                        deploy_resp = requests.put(
                            f"{self.api_base_url}/api/v1/devices/{config.device_id}/deploy",
                            headers=headers,
                            json={"location": config.base_location, "notes": "Auto-deployed by simulator"},
                            timeout=30
                        )
                        if deploy_resp.status_code == 200:
                            print("     Deployed successfully.")
                        else:
                            print(f"     Failed to deploy: {deploy_resp.status_code}")
                            
                else:
                    print(f"  ✨ Creating new device '{config.device_name}'...")
                    create_payload = {
                        "name": config.device_name,
                        "type": config.device_type.lower(),
                        "serial_number": config.serial_number,
                        "description": "Auto-generated simulated device",
                        "location": config.base_location,
                        "specifications": "{}"
                    }
                    resp = requests.post(
                        f"{self.api_base_url}/api/v1/devices/",
                        headers=headers,
                        json=create_payload,
                        timeout=30
                    )
                    
                    if resp.status_code in [200, 201]:
                        new_dev = resp.json()
                        config.device_id = new_dev['id']
                        print(f"     Created ID: {new_dev['id']}")
                        
                        # Now Deploy status is needed
                        print(f"  🚀 Initial deployment for {new_dev['id']}...")
                        requests.put(
                            f"{self.api_base_url}/api/v1/devices/{new_dev['id']}/deploy",
                            headers=headers,
                            json={"location": config.base_location, "notes": "Initial auto-deployment"},
                            timeout=30
                        )
                    else:
                        print(f"     ❌ Failed to create: {resp.status_code} - {resp.text}")

        except Exception as e:
            print(f"❌ Provisioning error: {e}")
            print("⚠️ Continuing with existing devices or trying to create new ones...")
        print("Provisioning complete.\n")


    async def simulate_telemetry(self, device: DeviceConfig):
        """Generate and send telemetry data for a device."""
        print(f"📡 Telemetry active: {device.device_name} (ID: {device.device_id})")
        
        while self.running:
            try:
                telemetry = self._generate_telemetry(device)
                
                headers = {"Content-Type": "application/json"}
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                
                response = await self._send_request(
                    "POST",
                    f"{self.api_base_url}/api/v1/devices/telemetry",
                    json=telemetry,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 401:
                    print("Token expired, re-authenticating...")
                    if self.authenticate():
                        continue
                elif response.status_code not in [200, 201]:
                    print(f"⚠️ Telemetry failed ID {device.device_id}: {response.status_code}")
                    # If 404/400, maybe it was deleted or recalled? 
                    if response.status_code in [404, 400]:
                         print(f"     Pausing telemetry for {device.device_name} (check status)")
                         await asyncio.sleep(10)
                    
            except Exception as e:
                print(f"Error sending telemetry for {device.device_name}: {e}")
            
            await asyncio.sleep(device.interval_seconds)

    async def simulate_events(self, device: DeviceConfig):
        """Randomly generate events/alerts."""
        # print(f"🔔 Events active: {device.device_name}")
        while self.running:
            # Events happen randomly every 15-45 seconds
            await asyncio.sleep(random.uniform(15, 45))
            
            if random.random() < 0.4: # 40% chance
                try:
                    event_type = random.choice([
                        "low_battery", "connection_lost", "error", "warning", 
                        "firmware_update", "motion_detected", "door_opened"
                    ])
                    
                    messages = {
                        "low_battery": "Battery level critical (15%)",
                        "connection_lost": "Signal strength dropped below threshold",
                        "error": "Sensor malfunction: read error",
                        "warning": "Operating temperature high",
                        "motion_detected": "Movement detected in restricted zone",
                        "door_opened": "Main casing opened unexpectedly"
                    }

                    event_data = {
                        "device_id": device.device_id,
                        "event_type": event_type,
                        "message": messages.get(event_type, f"Event {event_type} occurred"),
                        "timestamp": datetime.utcnow().isoformat(),
                        "details": {
                            "value": random.randint(1, 100),
                            "severity": "high" if event_type in ["error", "connection_lost"] else "info"
                        }
                    }
                    
                    headers = {"Content-Type": "application/json"}
                    
                    response = await self._send_request(
                        "POST",
                        f"{self.api_base_url}/api/v1/devices/events",
                        json=event_data,
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code in [200, 201]:
                        print(f"⚡ EVENT: {event_type} -> {device.device_name}")
                        
                except Exception as e:
                    print(f"Error sending event for {device.device_name}: {e}")

    def _generate_telemetry(self, device: DeviceConfig) -> Dict:
        """Generate realistic telemetry data."""
        base_data = {
            "device_id": device.device_id,
            "device_name": device.device_name,
            "timestamp": datetime.utcnow().isoformat(),
            "location": device.base_location
        }
        
        if device.device_type == "SENSOR":
            # Simulate daily temperature cycle + noise
            t = time.time()
            base_temp = 22 + 5 * (1 if (t % 60) < 30 else -1) # Fluctuate
            
            base_data.update({
                "temperature": round(base_temp + random.uniform(-1, 1), 2),
                "humidity": round(random.uniform(40, 60), 2),
                "pressure": round(random.uniform(1010, 1015), 2),
                "battery_level": round(random.uniform(80, 99), 1),
            })
        elif device.device_type == "CAMERA":
            base_data.update({
                "fps": random.randint(24, 30),
                "status": "recording"
            })
        else:
            base_data.update({
                "value": round(random.uniform(0, 100), 2)
            })
        
        return base_data

    async def start(self):
        """Start simulating all devices."""
        self.running = True
        
        # Initial auth
        if not self.authenticate():
            return
            
        # Provision devices (Create if not exist)
        self.provision_devices()
        
        tasks = []
        for device in self.devices:
            if device.device_id: # Only start if we have a valid ID
                tasks.append(self.simulate_telemetry(device))
                tasks.append(self.simulate_events(device))
            else:
                print(f"Skipping {device.device_name} - No ID found.")
        
        print("🚀 Simulation running...")
        await asyncio.gather(*tasks)

    def stop(self):
        self.running = False
        print("\nStopping simulation...")


async def main():
    simulator = IoTSimulator()
    
    # Define devices with fixed Serial Numbers so we can find them again
    
    # 1. Warehouse Sensor
    simulator.add_device(DeviceConfig(
        device_id=0, # Will be ignored/filled
        device_name="Warehouse Temp A1",
        device_type="SENSOR",
        base_location="Warehouse A",
        interval_seconds=1.0,
        serial_number="SN-WH-A1-001"
    ))
    
    # 2. Camera (Mapped to SENSOR for backend compatibility)
    simulator.add_device(DeviceConfig(
        device_id=0,
        device_name="Entrance Cam Cam-01",
        device_type="SENSOR", 
        base_location="Main Entrance",
        interval_seconds=2.0,
        serial_number="SN-CAM-01-002"
    ))
    
    # 3. Office Sensor
    simulator.add_device(DeviceConfig(
        device_id=0,
        device_name="Office 2B Thermostat",
        device_type="SENSOR",
        base_location="Office Floor 2",
        interval_seconds=3.0,
        serial_number="SN-OFF-2B-003"
    ))

    # 4. Parking Light
    simulator.add_device(DeviceConfig(
        device_id=0,
        device_name="Parking Lot Light",
        device_type="ACTUATOR",
        base_location="Parking B",
        interval_seconds=5.0,
        serial_number="SN-PK-L1-004"
    ))

    try:
        await simulator.start()
    except KeyboardInterrupt:
        simulator.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
