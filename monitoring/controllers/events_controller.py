"""
Events Controller for Monitoring microservice.
Handles all HTTP endpoints related to device events.
"""

from fastapi import APIRouter, Query
from typing import Optional, List
from dto.events_dto import EventResponse
from dal.events_dao import EventsDAO

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=List[EventResponse])
def get_events(
    device_id: Optional[int] = Query(None, description="Filter by device ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return")
):
    """
    Get device events.
    
    Args:
        device_id: Optional device ID to filter by
        event_type: Optional event type to filter by
        limit: Maximum number of records to return (default 100)
    
    Returns:
        List of event records
    """
    return EventsDAO.get_all(
        device_id=device_id,
        event_type=event_type,
        limit=limit
    )


@router.get("/stats")
def get_events_stats():
    """
    Get events statistics.
    
    Returns:
        Statistics about stored events
    """
    return EventsDAO.get_stats()
