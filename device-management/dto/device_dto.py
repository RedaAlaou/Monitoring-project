"""
Data Transfer Objects (DTOs) for Device Management API.
Defines request and response models using Pydantic.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class DeviceStatusDto(str, Enum):
    """Device status enumeration for API."""
    IN_STOCK = "in_stock"
    RESERVED = "reserved"
    DEPLOYED = "deployed"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class DeviceTypeDto(str, Enum):
    """Device type enumeration for API."""
    # Legacy types (backward compatibility)
    SENSOR = "sensor"
    GATEWAY = "gateway"
    ACTUATOR = "actuator"
    CONTROLLER = "controller"
    OTHER = "other"
    
    # New explicit IoT types
    IOT_SENSOR = "iot_sensor"
    IOT_GATEWAY = "iot_gateway"
    IOT_ACTUATOR = "iot_actuator"
    
    # New system/computer types
    COMPUTER = "computer"
    SERVER = "server"
    EDGE_DEVICE = "edge_device"
    GPU_NODE = "gpu_node"


class DeviceRequest(BaseModel):
    """Request model for creating a new device."""
    name: str = Field(..., min_length=1, max_length=100, description="Device name")
    type: DeviceTypeDto = Field(..., description="Device type")
    serial_number: str = Field(..., min_length=1, max_length=100, description="Unique serial number")
    description: Optional[str] = Field(None, description="Device description")
    location: Optional[str] = Field(None, max_length=100, description="Device location")
    specifications: Optional[str] = Field(None, description="Device specifications as JSON string")


class DeviceResponse(BaseModel):
    """Response model for device data."""
    id: int
    name: str
    type: str
    serial_number: str
    description: Optional[str]
    status: str
    location: Optional[str]
    specifications: Optional[str]
    purchase_date: Optional[str]
    deploy_date: Optional[str]
    last_maintenance_date: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Response model for list of devices."""
    devices: List[DeviceResponse]
    total: int
    page: int
    page_size: int


class DeviceUpdateRequest(BaseModel):
    """Request model for updating a device."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    specifications: Optional[str] = None


class DeviceStatusUpdateRequest(BaseModel):
    """Request model for updating device status."""
    status: DeviceStatusDto = Field(..., description="New device status")
    location: Optional[str] = Field(None, max_length=100, description="New location if deploying")
    notes: Optional[str] = Field(None, description="Notes about the status change")


class DeployRequest(BaseModel):
    """Request model for deploying a device to the field."""
    location: str = Field(..., max_length=100, description="Deployment location")
    notes: Optional[str] = Field(None, description="Deployment notes")


class RecallRequest(BaseModel):
    """Request model for recalling a device from the field."""
    location: Optional[str] = Field(None, max_length=100, description="New location (warehouse)")
    notes: Optional[str] = Field(None, description="Recall notes")


class MaintenanceRequest(BaseModel):
    """Request model for sending device to maintenance."""
    notes: Optional[str] = Field(None, description="Maintenance notes")


class ReserveRequest(BaseModel):
    """Request model for reserving a device."""
    notes: Optional[str] = Field(None, description="Reservation notes")


class TelemetryRequest(BaseModel):
    """Model for incoming telemetry data from devices."""
    device_id: int
    device_name: Optional[str] = None
    timestamp: Optional[str] = None
    location: Optional[str] = None
    
    class Config:
        extra = "allow"


class DeviceEventRequest(BaseModel):
    """Model for incoming device events (alerts/errors)."""
    device_id: int
    event_type: str = Field(..., description="Type of event e.g. error, warning, low_battery")
    timestamp: Optional[str] = None
    details: Optional[dict] = None

    class Config:
        extra = "allow"


class ActionResponse(BaseModel):
    """Generic response for action operations."""
    success: bool
    message: str
    device: Optional[DeviceResponse] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
