"""
Computer Performance Monitoring Client
Monitors system resources (CPU, RAM, GPU, Disk) and sends telemetry to the IoT platform.
"""

import os
import sys
import time
import socket
import psutil
import requests
import json
from datetime import datetime
from typing import Dict, Optional

# Add device_client to path
sys.path.insert(0, os.path.dirname(__file__))

# Configuration
SIGNING_SERVICE_URL = os.getenv("SIGNING_SERVICE_URL", "http://localhost:8000")
DEVICE_MANAGEMENT_URL = os.getenv("DEVICE_MANAGEMENT_URL", "http://localhost:8001")
MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", "5"))  # seconds

# Device configuration
DEVICE_NAME = os.getenv("DEVICE_NAME", f"Computer-{socket.gethostname()}")
DEVICE_SERIAL = os.getenv("DEVICE_SERIAL", f"PC-{socket.gethostname().upper()}")
DEVICE_TYPE = "computer"  # New device type
DEVICE_LOCATION = os.getenv("DEVICE_LOCATION", "Office")


class ComputerMonitor:
    """Monitor system performance and send telemetry."""
    
    def __init__(self):
        """Initialize the computer monitor."""
        self.device_id: Optional[int] = None
        self.jwt_token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Try to import GPU monitoring (optional)
        self.gpu_available = False
        try:
            import GPUtil
            self.GPUtil = GPUtil
            self.gpu_available = True
            print("✓ GPU monitoring enabled (NVIDIA)")
        except ImportError:
            print("⚠ GPU monitoring unavailable (install GPUtil for NVIDIA support)")
    
    def authenticate(self, username: str = "admin@example.com", password: str = "admin123") -> bool:
        """
        Authenticate with the signing service.
        
        Args:
            username: User email
            password: User password
            
        Returns:
            True if authentication successful
        """
        try:
            response = self.session.post(
                f"{SIGNING_SERVICE_URL}/users/auth",
                json={"email": username, "password": password},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("token")
                if not self.jwt_token:
                    print(f"✗ No token in response: {data}")
                    return False
                self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})
                print(f"✓ Authenticated as {username}")
                print(f"  Token preview: {self.jwt_token[:50]}...")
                return True
            else:
                print(f"✗ Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Authentication error: {e}")
            return False
    
    def get_device_by_serial(self) -> Optional[Dict]:
        """
        Check if device exists by serial number.
        
        Returns:
            Device data if found, None otherwise
        """
        try:
            # List all devices and search for matching serial
            # Use page_size=100 to get more devices at once
            response = self.session.get(
                f"{DEVICE_MANAGEMENT_URL}/api/v1/devices",
                params={"page_size": 100},
                timeout=30
            )
            
            print(f"  Checking for existing device (status: {response.status_code})")
            
            if response.status_code == 200:
                data = response.json()
                # Handle DeviceListResponse structure
                if isinstance(data, dict) and 'devices' in data:
                    devices = data['devices']
                    print(f"  Found {len(devices)} devices in registry")
                elif isinstance(data, list):
                    devices = data
                    print(f"  Found {len(devices)} devices in registry")
                else:
                    print(f"  Unexpected response format: {type(data)}")
                    return None
                    
                for device in devices:
                    if device.get("serial_number") == DEVICE_SERIAL:
                        print(f"✓ Found existing device: {device['name']} (ID: {device['id']})")
                        return device
                print(f"  Device with serial {DEVICE_SERIAL} not found in registry")
            else:
                print(f"  Failed to fetch devices: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            print(f"✗ Error checking device: {e}")
            return None
    
    def provision_device(self) -> bool:
        """
        Create device if not exists, then deploy it.
        
        Returns:
            True if provisioning successful
        """
        # Check if device exists
        existing_device = self.get_device_by_serial()
        
        if existing_device:
            self.device_id = existing_device['id']
            
            # Auto-deploy if not deployed
            if existing_device.get('status') != 'deployed':
                return self.deploy_device()
            return True
        
        # Create new device
        try:
            device_data = {
                "name": DEVICE_NAME,
                "type": DEVICE_TYPE,
                "serial_number": DEVICE_SERIAL,
                "description": f"System monitoring computer - {socket.gethostname()}",
                "location": DEVICE_LOCATION,
                "specifications": json.dumps({
                    "hostname": socket.gethostname(),
                    "os": sys.platform,
                    "cpu_cores": psutil.cpu_count(),
                    "total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 2)
                })
            }
            
            print(f"  Creating device with type: {DEVICE_TYPE}")
            print(f"  Authorization header: Bearer {self.jwt_token[:30]}...")
            
            response = self.session.post(
                f"{DEVICE_MANAGEMENT_URL}/api/v1/devices",
                json=device_data,
                timeout=45
            )
            
            print(f"  Response status: {response.status_code}")
            
            if response.status_code in (200, 201):
                device = response.json()
                self.device_id = device['id']
                print(f"✓ Device created: {DEVICE_NAME} (ID: {self.device_id})")
                
                # Auto-deploy
                return self.deploy_device()
            else:
                print(f"✗ Device creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Device provisioning error: {e}")
            return False
    
    def deploy_device(self) -> bool:
        """
        Deploy the device (change status to deployed).
        
        Returns:
            True if deployment successful
        """
        try:
            response = self.session.put(
                f"{DEVICE_MANAGEMENT_URL}/api/v1/devices/{self.device_id}/deploy",
                json={"location": DEVICE_LOCATION},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✓ Device deployed (ID: {self.device_id})")
                return True
            else:
                print(f"✗ Device deployment failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Device deployment error: {e}")
            return False
    
    def read_system_metrics(self) -> Dict:
        """
        Read current system performance metrics.
        
        Returns:
            Dictionary with system metrics
        """
        metrics = {
            # CPU metrics
            "cpu_usage": psutil.cpu_percent(interval=1),
            "cpu_per_core": psutil.cpu_percent(interval=0.5, percpu=True),
            
            # Memory metrics
            "ram_used_mb": psutil.virtual_memory().used / (1024**2),
            "ram_percent": psutil.virtual_memory().percent,
            
            # Disk metrics
            "disk_usage_percent": psutil.disk_usage('/').percent,
            
            # Network metrics
            "network_sent_mb": psutil.net_io_counters().bytes_sent / (1024**2),
            "network_recv_mb": psutil.net_io_counters().bytes_recv / (1024**2),
        }
        
        # GPU metrics (if available)
        if self.gpu_available:
            try:
                gpus = self.GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Use first GPU
                    metrics["gpu_usage"] = gpu.load * 100  # Convert to percentage
                    metrics["gpu_memory_used_mb"] = gpu.memoryUsed
                    metrics["gpu_temperature"] = gpu.temperature
            except Exception as e:
                print(f"⚠ GPU metrics error: {e}")
        
        return metrics
    
    def send_telemetry(self, metrics: Dict) -> bool:
        """
        Send telemetry data to device management service.
        
        Args:
            metrics: System metrics dictionary
            
        Returns:
            True if sending successful
        """
        try:
            telemetry_data = {
                "device_id": self.device_id,
                "device_name": DEVICE_NAME,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "location": DEVICE_LOCATION,
                **metrics
            }
            
            response = self.session.post(
                f"{DEVICE_MANAGEMENT_URL}/api/v1/devices/telemetry",
                json=telemetry_data,
                timeout=15
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"✗ Telemetry send failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Telemetry send error: {e}")
            return False
    
    def run(self):
        """Main monitoring loop."""
        print("=" * 60)
        print("Computer Performance Monitor")
        print("=" * 60)
        
        # Authenticate
        if not self.authenticate():
            print("\n✗ Failed to authenticate. Exiting.")
            return
        
        # Provision device
        if not self.provision_device():
            print("\n✗ Failed to provision device. Exiting.")
            return
        
        print(f"\n✓ Monitoring started (interval: {MONITORING_INTERVAL}s)")
        print(f"  Device ID: {self.device_id}")
        print(f"  Device Name: {DEVICE_NAME}")
        print(f"  Serial: {DEVICE_SERIAL}")
        print(f"  Type: {DEVICE_TYPE}")
        print("\nPress Ctrl+C to stop...\n")
        
        telemetry_count = 0
        
        try:
            while True:
                # Read system metrics
                metrics = self.read_system_metrics()
                
                # Send telemetry
                if self.send_telemetry(metrics):
                    telemetry_count += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Telemetry #{telemetry_count} sent | "
                          f"CPU: {metrics['cpu_usage']:.1f}% | "
                          f"RAM: {metrics['ram_percent']:.1f}% | "
                          f"Disk: {metrics['disk_usage_percent']:.1f}%"
                          + (f" | GPU: {metrics.get('gpu_usage', 0):.1f}%" if 'gpu_usage' in metrics else ""))
                
                # Wait for next interval
                time.sleep(MONITORING_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n\n✓ Monitoring stopped by user")
        except Exception as e:
            print(f"\n✗ Monitoring error: {e}")


if __name__ == "__main__":
    monitor = ComputerMonitor()
    monitor.run()
