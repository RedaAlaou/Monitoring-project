"""
Configuration for Monitoring microservice.
"""
import os
from typing import Final

# MongoDB Configuration
MONGODB_URL: Final[str] = os.getenv("MONGODB_URL", "mongodb://localhost:27018")
MONGODB_DB: Final[str] = os.getenv("MONGODB_DB", "monitoring")
TELEMETRY_COLLECTION: Final[str] = os.getenv("TELEMETRY_COLLECTION", "telemetry")
DEVICE_EVENTS_COLLECTION: Final[str] = os.getenv("DEVICE_EVENTS_COLLECTION", "device_events")

# RabbitMQ Configuration
RABBITMQ_HOST: Final[str] = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT: Final[int] = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER: Final[str] = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD: Final[str] = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_VHOST: Final[str] = os.getenv("RABBITMQ_VHOST", "/")

# Exchange and Queue Names - MUST MATCH device-management publisher
MONITORING_EXCHANGE: Final[str] = os.getenv("MONITORING_EXCHANGE", "device_events")
TELEMETRY_QUEUE: Final[str] = os.getenv("TELEMETRY_QUEUE", "monitoring_telemetry")
TELEMETRY_ROUTING_KEY: Final[str] = "device.telemetry"
DEVICE_EVENTS_QUEUE: Final[str] = os.getenv("DEVICE_EVENTS_QUEUE", "monitoring_device_events")
DEVICE_EVENT_ROUTING_KEY: Final[str] = "device.event"

# Socket.IO Configuration
SOCKETIO_CORS_ORIGINS: Final[str] = os.getenv("SOCKETIO_CORS_ORIGINS", "*")

# Logging Configuration
import logging

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(logs_dir, exist_ok=True)

_formatter = logging.Formatter(fmt="%(asctime)s-%(levelname)s-%(message)s")

# Console handler for Docker logs
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_formatter)

# File handler
_file_handler = logging.FileHandler(os.path.join(logs_dir, "monitoring.log"))
_file_handler.setFormatter(_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(_console_handler)  # Add console output
logger.addHandler(_file_handler)
