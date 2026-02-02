"""
MongoDB Client for Monitoring microservice.
Handles MongoDB connection and database access.
"""

import pymongo
from config.settings import (
    MONGODB_URL,
    MONGODB_DB,
    TELEMETRY_COLLECTION,
    DEVICE_EVENTS_COLLECTION,
    logger
)

# MongoDB Client
mongo_client = pymongo.MongoClient(MONGODB_URL)

# Database instance
db = mongo_client[MONGODB_DB]

# Collections
telemetry_collection = db[TELEMETRY_COLLECTION]
events_collection = db[DEVICE_EVENTS_COLLECTION]


def get_db():
    """Get database instance."""
    return db


def get_telemetry_collection():
    """Get telemetry collection."""
    return telemetry_collection


def get_events_collection():
    """Get events collection."""
    return events_collection


def close_connection():
    """Close MongoDB connection."""
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")
