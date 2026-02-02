"""
Device entity models for the Device Management Microservice.
Defines the database tables using SQLAlchemy ORM.
"""

from enum import Enum as PyEnum
from helpers.config import Base
from sqlalchemy import Column, String, Integer, DateTime, func, Text, Enum


class DeviceStatus(PyEnum):
    """Enumeration of possible device statuses."""
    IN_STOCK = "in_stock"
    RESERVED = "reserved"
    DEPLOYED = "deployed"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class DeviceType(PyEnum):
    """Enumeration of device types.
    
    Supports both legacy and new explicit categories:
    - Legacy: sensor, gateway, actuator, controller, other
    - IoT Devices: iot_sensor, iot_gateway, iot_actuator
    - System Devices: computer, server, edge_device, gpu_node
    
    Legacy values are automatically mapped to new categories for backward compatibility.
    """
    # Legacy values (for backward compatibility)
    SENSOR = "sensor"
    GATEWAY = "gateway"
    ACTUATOR = "actuator"
    CONTROLLER = "controller"
    
    # New explicit IoT categories
    IOT_SENSOR = "iot_sensor"
    IOT_GATEWAY = "iot_gateway"
    IOT_ACTUATOR = "iot_actuator"
    
    # New explicit System categories
    COMPUTER = "computer"
    SERVER = "server"
    EDGE_DEVICE = "edge_device"
    GPU_NODE = "gpu_node"
    
    # Fallback
    OTHER = "other"
    
    @classmethod
    def normalize(cls, value: str) -> 'DeviceType':
        """Normalize legacy device types to new categories.
        
        Maps:
        - 'sensor' → 'iot_sensor'
        - 'gateway' → 'iot_gateway'
        - 'actuator' → 'iot_actuator'
        - 'controller' → 'computer'
        - Other values returned as-is
        
        Args:
            value: Device type string value
            
        Returns:
            DeviceType enum value
        """
        legacy_mapping = {
            'sensor': 'iot_sensor',
            'gateway': 'iot_gateway',
            'actuator': 'iot_actuator',
            'controller': 'computer',
        }
        normalized = legacy_mapping.get(value, value)
        try:
            return cls(normalized)
        except ValueError:
            return cls.OTHER
    
    @property
    def is_iot(self) -> bool:
        """Check if device is IoT type."""
        return self in (
            self.SENSOR, self.GATEWAY, self.ACTUATOR,  # Legacy
            self.IOT_SENSOR, self.IOT_GATEWAY, self.IOT_ACTUATOR  # New
        )
    
    @property
    def is_system(self) -> bool:
        """Check if device is system/computer type."""
        return self in (
            self.CONTROLLER, self.COMPUTER, self.SERVER, self.EDGE_DEVICE, self.GPU_NODE  # Controllers + new system types
        )


class Device(Base):
    """
    Device entity representing IoT devices in the system.
    Maps to the t_devices table in the database.
    """
    __tablename__ = 't_devices'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(DeviceType), nullable=False, default=DeviceType.OTHER)
    serial_number = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(DeviceStatus), nullable=False, default=DeviceStatus.IN_STOCK)
    location = Column(String(100), nullable=True)  # Warehouse or deployment location
    specifications = Column(Text, nullable=True)  # JSON string for flexible specs
    purchase_date = Column(DateTime, nullable=True)
    deploy_date = Column(DateTime, nullable=True)
    last_maintenance_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    
    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', serial='{self.serial_number}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert device to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value if self.type else None,
            'serial_number': self.serial_number,
            'description': self.description,
            'status': self.status.value if self.status else None,
            'location': self.location,
            'specifications': self.specifications,
            'purchase_date': str(self.purchase_date) if self.purchase_date else None,
            'deploy_date': str(self.deploy_date) if self.deploy_date else None,
            'last_maintenance_date': str(self.last_maintenance_date) if self.last_maintenance_date else None,
            'created_at': str(self.created_at) if self.created_at else None,
            'updated_at': str(self.updated_at) if self.updated_at else None
        }


class DeviceLog(Base):
    """
    Device log entity for tracking device lifecycle changes.
    Maps to the t_device_logs table in the database.
    """
    __tablename__ = 't_device_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    device_id = Column(Integer, nullable=False, index=True)
    action = Column(String(50), nullable=False)
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=True)
    performed_by = Column(Integer, nullable=True)  # User ID
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<DeviceLog(id={self.id}, device_id={self.device_id}, action='{self.action}')>"
