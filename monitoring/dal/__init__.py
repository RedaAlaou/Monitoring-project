"""DAL (Data Access Layer) package for Monitoring microservice."""
from dal.mongo_client import mongo_client, db
from dal.telemetry_dao import TelemetryDAO
from dal.events_dao import EventsDAO

__all__ = ["mongo_client", "db", "TelemetryDAO", "EventsDAO"]
