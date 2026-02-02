"""
Events DTOs (Data Transfer Objects) for Monitoring microservice.
Defines request and response models for device events.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class DeviceEvent(BaseModel):
    """Model for incoming device events."""
    device_id: int
    event_type: str
    timestamp: Optional[str] = None
    details: Dict[str, Any] = {}


class EventResponse(BaseModel):
    """Response model for device events."""
    id: str
    device_id: int
    event_type: str
    timestamp: str
    details: Dict[str, Any] = {}


class EventStats(BaseModel):
    """Statistics about device events."""
    events_count: int
    total_devices: int
    devices: list


class EventTypes:
    """Event type constants."""
    DEPLOYED = "deployed"
    RECALLED = "recalled"
    MAINTENANCE = "maintenance"
    STATUS_CHANGE = "status_change"
    ALERT = "alert"
    ERROR = "error"
    INFO = "info"
