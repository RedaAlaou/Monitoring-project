"""
Telemetry Controller for Monitoring microservice.
Handles all HTTP endpoints related to device telemetry data.
"""

from fastapi import APIRouter, Query
from typing import Optional, List
from dto.telemetry_dto import TelemetryResponse
from dal.telemetry_dao import TelemetryDAO

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.get("/", response_model=List[TelemetryResponse])
def get_telemetry(
    device_id: Optional[int] = Query(None, description="Filter by device ID"),
    device_type: Optional[str] = Query(None, description="Filter by device type (e.g., 'iot_sensor', 'computer')"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return")
):
    """
    Get telemetry data from devices.
    
    Args:
        device_id: Optional device ID to filter by
        device_type: Optional device type to filter by
        limit: Maximum number of records to return (default 100)
    
    Returns:
        List of telemetry records
    """
    return TelemetryDAO.get_all(device_id=device_id, device_type=device_type, limit=limit)


@router.get("/stats")
def get_telemetry_stats():
    """
    Get telemetry statistics.
    
    Returns:
        Statistics about stored telemetry data
    """
    return TelemetryDAO.get_stats()
