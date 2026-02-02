#!/usr/bin/env python3
"""
End Device Client
Example client code for physical IoT devices to communicate with the system.
Uses MQTT or HTTP to send data.
"""

import time
import json
import random
import paho.mqtt.client as mqtt
import requests
from typing import Dict, Optional
from datetime import datetime


class EndDeviceClient:
    """
    Client for IoT end devices to communicate with the monitoring system.
    Supports both MQTT and HTTP protocols.
    """
    
    def __init__(
        self,
        device_id: int,
        device_name: str,
        mqtt_broker: str = "localhost",
        mqtt_port: int = 1883,
        api_url: str = "http://localhost:8001"
    ):
        """
        Initialize the end device client.
        
        Args:
            device_id: Unique identifier for this device
            device_name: Human-readable name
            mqtt_broker: MQTT broker address
            mqtt_port: MQTT broker port
            api_url: Device Management API URL
        """
        self.device_id = device_id
        self.device_name = device_name
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.api_url = api_url
        
        self.mqtt_client = None
        self._connected = False

    def connect_mqtt(self, client_id: str = None) -> bool:
        """
        Connect to MQTT broker.
        
        Args:
            client_id: Unique client ID (defaults to device_name)
            
        Returns:
            True if connected successfully
        """
        if client_id is None:
            client_id = self.device_name
            
        self.mqtt_client = mqtt.Client(client_id=client_id)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        
        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            return True
        except Exception as e:
            print(f"MQTT connection failed: {e}")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            print(f"Connected to MQTT broker: {self.mqtt_broker}")
            self._connected = True
            
            # Subscribe to commands/topics for this device
            topic = f"devices/{self.device_id}/commands"
            self.mqtt_client.subscribe(topic)
            print(f"Subscribed to: {topic}")
        else:
            print(f"Failed to connect, return code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnect callback."""
        print(f"Disconnected from MQTT broker (code: {rc})")
        self._connected = False

    def publish_telemetry_http(self, data: Dict) -> bool:
        """
        Send telemetry data via HTTP.
        
        Args:
            data: Telemetry data dictionary
            
        Returns:
            True if successful
        """
        try:
            payload = {
                "device_id": self.device_id,
                "device_name": self.device_name,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            
            response = requests.post(
                f"{self.api_url}/api/v1/telemetry",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            print(f"HTTP publish failed: {e}")
            return False

    def publish_telemetry_mqtt(self, data: Dict) -> bool:
        """
        Send telemetry data via MQTT.
        
        Args:
            data: Telemetry data dictionary
            
        Returns:
            True if successful
        """
        if not self._connected:
            print("Not connected to MQTT broker")
            return False
            
        try:
            payload = {
                "device_id": self.device_id,
                "device_name": self.device_name,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            
            topic = f"devices/{self.device_id}/telemetry"
            self.mqtt_client.publish(topic, json.dumps(payload))
            return True
            
        except Exception as e:
            print(f"MQTT publish failed: {e}")
            return False

    def get_device_status(self) -> Optional[Dict]:
        """
        Get current device status from API.
        
        Returns:
            Device status dictionary or None
        """
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/devices/{self.device_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"Failed to get device status: {e}")
            return None

    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()


class SensorDevice(EndDeviceClient):
    """Specialized client for temperature/humidity sensors."""
    
    def read_sensor_data(self) -> Dict:
        """Read simulated sensor data."""
        return {
            "temperature": round(random.uniform(-20, 60), 2),
            "humidity": round(random.uniform(20, 80), 2),
            "pressure": round(random.uniform(950, 1050), 2),
            "battery_level": round(random.uniform(20, 100), 2),
        }
    
    def send_data(self, use_mqtt: bool = True) -> bool:
        """Read and send sensor data."""
        data = self.read_sensor_data()
        
        if use_mqtt:
            return self.publish_telemetry_mqtt(data)
        return self.publish_telemetry_http(data)


class CameraDevice(EndDeviceClient):
    """Specialized client for IP cameras."""
    
    def __init__(self, device_id: int, device_name: str, **kwargs):
        super().__init__(device_id, device_name, **kwargs)
    
    def read_camera_data(self) -> Dict:
        """Read simulated camera data."""
        return {
            "resolution": "1080p",
            "fps": random.randint(15, 30),
            "motion_detected": random.choice([True, False]),
            "storage_used": round(random.uniform(10, 500), 2),
        }
    
    def send_data(self, use_mqtt: bool = True) -> bool:
        """Read and send camera data."""
        data = self.read_camera_data()
        
        if use_mqtt:
            return self.publish_telemetry_mqtt(data)
        return self.publish_telemetry_http(data)


# Example usage
if __name__ == "__main__":
    # Example: Create a sensor device
    sensor = SensorDevice(
        device_id=1,
        device_name="Temperature Sensor 001",
        mqtt_broker="localhost",
        api_url="http://localhost:8001"
    )
    
    # Connect to MQTT
    sensor.connect_mqtt()
    
    # Send data every 5 seconds
    try:
        while True:
            sensor.send_data(use_mqtt=True)
            time.sleep(5)
    except KeyboardInterrupt:
        sensor.disconnect()
