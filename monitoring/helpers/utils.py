"""
Utility functions for Monitoring microservice.
"""

from datetime import datetime
from typing import Dict, Any
import uuid


def format_timestamp(timestamp: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format timestamp string to human-readable format.
    
    Args:
        timestamp: ISO format timestamp string
        format: Output format string
    
    Returns:
        Formatted timestamp string
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime(format)
    except (ValueError, AttributeError):
        return timestamp


def validate_device_data(data: Dict[str, Any]) -> bool:
    """
    Validate device data structure.
    
    Args:
        data: Device data dictionary
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["device_id"]
    
    for field in required_fields:
        if field not in data:
            return False
    
    if not isinstance(data["device_id"], int):
        return False
    
    return True


def generate_uuid() -> str:
    """
    Generate a unique identifier.
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def parse_iso_datetime(timestamp: str) -> datetime:
    """
    Parse ISO format timestamp to datetime object.
    
    Args:
        timestamp: ISO format timestamp string
    
    Returns:
        datetime object
    """
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return datetime.utcnow()


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        ISO format timestamp string
    """
    return datetime.utcnow().isoformat()
