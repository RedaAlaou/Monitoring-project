#!/usr/bin/env python3
"""
Script to insert test data into MongoDB for the monitoring service.
"""

from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27018")
db = client["monitoring"]

# Clear existing data
db.telemetry.delete_many({})
db.device_events.delete_many({})

# Insert telemetry data
telemetry_data = [
    {
        "device_id": 1,
        "device_type": "sensor",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {"temperature": 25.5, "humidity": 60}
    },
    {
        "device_id": 2,
        "device_type": "gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {"status": "online", "uptime": 3600}
    },
    {
        "device_id": 1,
        "device_type": "sensor",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {"temperature": 26.2, "humidity": 58}
    },
    {
        "device_id": 3,
        "device_type": "actuator",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {"state": "active", "pressure": 1013}
    },
    {
        "device_id": 2,
        "device_type": "gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {"status": "online", "uptime": 7200}
    }
]

# Insert device events
events_data = [
    {
        "device_id": 1,
        "event_type": "deployed",
        "timestamp": datetime.utcnow().isoformat(),
        "details": {"location": "Building A", "deployed_by": "admin"}
    },
    {
        "device_id": 1,
        "event_type": "status_change",
        "timestamp": datetime.utcnow().isoformat(),
        "details": {"old_status": "in_stock", "new_status": "deployed"}
    },
    {
        "device_id": 2,
        "event_type": "maintenance",
        "timestamp": datetime.utcnow().isoformat(),
        "details": {"location": "Service Center", "reason": "Regular checkup"}
    },
    {
        "device_id": 3,
        "event_type": "deployed",
        "timestamp": datetime.utcnow().isoformat(),
        "details": {"location": "Building B", "deployed_by": "admin"}
    },
    {
        "device_id": 1,
        "event_type": "alert",
        "timestamp": datetime.utcnow().isoformat(),
        "details": {"alert_type": "high_temperature", "value": 30.0}
    }
]

# Insert data
telemetry_result = db.telemetry.insert_many(telemetry_data)
events_result = db.device_events.insert_many(events_data)

print(f"Inserted {len(telemetry_result.inserted_ids)} telemetry records")
print(f"Inserted {len(events_result.inserted_ids)} event records")

# Verify
print(f"\nTotal telemetry records: {db.telemetry.count_documents({})}")
print(f"Total event records: {db.device_events.count_documents({})}")

# Close connection
client.close()
print("\nTest data inserted successfully!")
