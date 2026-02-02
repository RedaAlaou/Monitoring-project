"""
Telemetry DTOs (Data Transfer Objects) for Monitoring microservice.
Defines request and response models for telemetry data.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class TelemetryData(BaseModel):
    """Model for incoming telemetry data from devices."""
    device_id: int
    device_name: Optional[str] = None
    timestamp: Optional[str] = None
    location: Optional[str] = None
    
    # Allow extra fields for dynamic telemetry metrics
    class Config:
        extra = "allow"


class TelemetryResponse(BaseModel):
    """Response model for telemetry data."""
    id: str
    device_id: int
    device_name: Optional[str] = None
    timestamp: str
    location: Optional[str] = None
    
    # Using a catch-all for extra data fields if needed, 
    # or just allowing extra fields in the response too.
    class Config:
        extra = "allow"


class TelemetryStats(BaseModel):
    """Statistics about telemetry data."""
    telemetry_count: int
    total_devices: int
    devices: list
