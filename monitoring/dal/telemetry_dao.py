"""
Telemetry DAO (Data Access Object) for Monitoring microservice.
Handles all database operations for telemetry data.
"""

from typing import Optional, List
from datetime import datetime
from dal.mongo_client import telemetry_collection
from dto.telemetry_dto import TelemetryResponse
from config.settings import logger


class TelemetryDAO:
    """Data Access Object for telemetry data operations."""

    @staticmethod
    def insert(data: dict) -> str:
        """
        Insert telemetry data into MongoDB.
        
        Args:
            data: Telemetry data dictionary
        
        Returns:
            Inserted document ID as string
        """
        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()
        
        result = telemetry_collection.insert_one(data)
        logger.info(f"Telemetry stored: device {data.get('device_id')}")
        return str(result.inserted_id)

    @staticmethod
    def get_all(device_id: Optional[int] = None, device_type: Optional[str] = None, limit: int = 100) -> List[TelemetryResponse]:
        """
        Get telemetry data with optional filtering.
        
        Args:
            device_id: Optional device ID to filter by
            device_type: Optional device type to filter by (e.g., 'iot_sensor', 'computer')
            limit: Maximum number of records to return
        
        Returns:
            List of TelemetryResponse objects
        """
        query = {}
        if device_id:
            query["device_id"] = device_id
        if device_type:
            query["device_type"] = device_type
        
        cursor = (
            telemetry_collection
            .find(query)
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        results = []
        for doc in cursor:
            # Flatten or handle data fields for the response
            doc_id = str(doc.pop("_id"))
            device_id = doc.pop("device_id")
            timestamp = doc.pop("timestamp")
            device_name = doc.pop("device_name", None)
            location = doc.pop("location", None)
            
            # The rest of the fields are telemetry metrics (the "data")
            results.append(TelemetryResponse(
                id=doc_id,
                device_id=device_id,
                timestamp=timestamp,
                device_name=device_name,
                location=location,
                **doc # Pass the remaining fields as extra attributes
            ))
        
        return results

    @staticmethod
    def count() -> int:
        """
        Get total count of telemetry records.
        
        Returns:
            Total count of telemetry records
        """
        return telemetry_collection.count_documents({})

    @staticmethod
    def get_distinct_devices() -> List[int]:
        """
        Get list of distinct device IDs in telemetry.
        
        Returns:
            List of device IDs
        """
        return telemetry_collection.distinct("device_id")

    @staticmethod
    def get_stats() -> dict:
        """
        Get telemetry statistics.
        
        Returns:
            Dictionary with telemetry statistics
        """
        count = TelemetryDAO.count()
        devices = TelemetryDAO.get_distinct_devices()
        
        return {
            "total_count": count,
            "device_count": len(devices),
            "telemetry_count": count,  # Keep old key for backward compat just in case
            "total_devices": len(devices), # Keep old key
            "devices": devices
        }

    @staticmethod
    def delete_old_data(days: int = 30) -> int:
        """
        Delete telemetry data older than specified days.
        
        Args:
            days: Number of days to keep data for
        
        Returns:
            Number of deleted documents
        """
        cutoff_date = datetime.utcnow()
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        result = telemetry_collection.delete_many({
            "timestamp": {"$lt": cutoff_date.isoformat()}
        })
        
        logger.info(f"Deleted {result.deleted_count} old telemetry records")
        return result.deleted_count
