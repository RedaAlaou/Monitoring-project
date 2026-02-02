"""
Events DAO (Data Access Object) for Monitoring microservice.
Handles all database operations for device events.
"""

from typing import Optional, List
from datetime import datetime
from dal.mongo_client import events_collection
from dto.events_dto import EventResponse
from config.settings import logger


class EventsDAO:
    """Data Access Object for device events operations."""

    @staticmethod
    def insert(data: dict) -> str:
        """
        Insert device event into MongoDB.
        
        Args:
            data: Event data dictionary
        
        Returns:
            Inserted document ID as string
        """
        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()
        
        result = events_collection.insert_one(data)
        logger.info(
            f"Device event stored: {data.get('event_type')} for device {data.get('device_id')}"
        )
        return str(result.inserted_id)

    @staticmethod
    def get_all(
        device_id: Optional[int] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[EventResponse]:
        """
        Get device events with optional filtering.
        
        Args:
            device_id: Optional device ID to filter by
            event_type: Optional event type to filter by
            limit: Maximum number of records to return
        
        Returns:
            List of EventResponse objects
        """
        query = {}
        if device_id:
            query["device_id"] = device_id
        if event_type:
            query["event_type"] = event_type
        
        cursor = (
            events_collection
            .find(query)
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        results = []
        for doc in cursor:
            results.append(EventResponse(
                id=str(doc["_id"]),
                device_id=doc["device_id"],
                event_type=doc.get("event_type", ""),
                timestamp=doc["timestamp"],
                details=doc.get("details", {})
            ))
        
        return results

    @staticmethod
    def count() -> int:
        """
        Get total count of event records.
        
        Returns:
            Total count of event records
        """
        return events_collection.count_documents({})

    @staticmethod
    def get_distinct_devices() -> List[int]:
        """
        Get list of distinct device IDs in events.
        
        Returns:
            List of device IDs
        """
        return events_collection.distinct("device_id")

    @staticmethod
    def get_stats() -> dict:
        """
        Get events statistics.
        
        Returns:
            Dictionary with events statistics
        """
        count = EventsDAO.count()
        devices = EventsDAO.get_distinct_devices()
        
        return {
            "events_count": count,
            "total_devices": len(devices),
            "devices": devices
        }

    @staticmethod
    def get_by_type(event_type: str, limit: int = 100) -> List[EventResponse]:
        """
        Get events by type.
        
        Args:
            event_type: Event type to filter by
            limit: Maximum number of records to return
        
        Returns:
            List of EventResponse objects
        """
        cursor = (
            events_collection
            .find({"event_type": event_type})
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        results = []
        for doc in cursor:
            results.append(EventResponse(
                id=str(doc["_id"]),
                device_id=doc["device_id"],
                event_type=doc.get("event_type", ""),
                timestamp=doc["timestamp"],
                details=doc.get("details", {})
            ))
        
        return results

    @staticmethod
    def delete_old_data(days: int = 30) -> int:
        """
        Delete event data older than specified days.
        
        Args:
            days: Number of days to keep data for
        
        Returns:
            Number of deleted documents
        """
        cutoff_date = datetime.utcnow()
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        result = events_collection.delete_many({
            "timestamp": {"$lt": cutoff_date.isoformat()}
        })
        
        logger.info(f"Deleted {result.deleted_count} old event records")
        return result.deleted_count
