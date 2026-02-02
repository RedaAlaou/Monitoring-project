"""
RabbitMQ Consumer Service for Monitoring microservice.
Handles consuming messages from RabbitMQ queues.
"""

import json
import threading
from datetime import datetime
import pika
import requests
from config.settings import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_VHOST,
    MONITORING_EXCHANGE,
    TELEMETRY_QUEUE,
    TELEMETRY_ROUTING_KEY,
    DEVICE_EVENTS_QUEUE,
    DEVICE_EVENT_ROUTING_KEY,
    logger
)
from dal.telemetry_dao import TelemetryDAO
from dal.events_dao import EventsDAO

# Device Management Service URL
DEVICE_MANAGEMENT_URL = "http://device-management:8001"

# In-memory cache for device types (to avoid repeated API calls)
_device_type_cache = {}


class RabbitMQConsumer:
    """RabbitMQ consumer for processing telemetry and device events."""

    def __init__(self):
        """Initialize RabbitMQ consumer."""
        self._connection = None
        self._channel = None
        self._is_running = False

    @staticmethod
    def _get_device_type(device_id: int) -> str:
        """
        Get device type from device management service.
        Uses in-memory cache to minimize API calls.
        
        Args:
            device_id: Device ID to look up
            
        Returns:
            Device type string (e.g., 'iot_sensor', 'computer')
        """
        global _device_type_cache
        
        # Check cache first
        if device_id in _device_type_cache:
            return _device_type_cache[device_id]
        
        # Fetch from device management API (public endpoint for type only)
        try:
            response = requests.get(
                f"{DEVICE_MANAGEMENT_URL}/api/v1/devices/{device_id}/type",
                timeout=5
            )
            if response.status_code == 200:
                device_data = response.json()
                device_type = device_data.get('type', 'other')
                _device_type_cache[device_id] = device_type
                logger.info(f"Fetched device type for device {device_id}: {device_type}")
                return device_type
            else:
                logger.warning(f"Failed to fetch device type for device {device_id}: {response.status_code}")
                return 'other'
        except Exception as e:
            logger.warning(f"Error fetching device type for device {device_id}: {e}")
            return 'other'

    def _get_connection_params(self) -> pika.ConnectionParameters:
        """Get RabbitMQ connection parameters."""
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        return pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host=RABBITMQ_VHOST,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
        )

    def _on_telemetry(self, channel, method, properties, body):
        """
        Callback for processing telemetry messages.
        
        Args:
            channel: RabbitMQ channel
            method: Delivery method
            properties: Message properties
            body: Message body
        """
        try:
            payload = json.loads(body)
            payload["timestamp"] = payload.get("timestamp", datetime.utcnow().isoformat())
            
            # Flatten 'data' field if it exists to match simulator output/standardized schema
            if "data" in payload and isinstance(payload["data"], dict):
                data_field = payload.pop("data")
                payload.update(data_field)
            
            # Enrich with device type from device management service
            device_id = payload.get('device_id')
            if device_id:
                device_type = self._get_device_type(device_id)
                payload['device_type'] = device_type
            
            # Store in MongoDB
            TelemetryDAO.insert(payload)
            
            # Emit via Socket.io (if callback is set)
            # Remove MongoDB _id before broadcasting (not JSON serializable)
            if hasattr(self, '_socketio_callback') and self._socketio_callback:
                broadcast_payload = {k: v for k, v in payload.items() if k != '_id'}
                self._socketio_callback("telemetry", broadcast_payload)
            
            logger.info(f"Telemetry stored: device {payload.get('device_id')}")
        except Exception as e:
            logger.error(f"Telemetry consumer error: {e}")
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def _on_device_event(self, channel, method, properties, body):
        """
        Callback for processing device event messages.
        
        Args:
            channel: RabbitMQ channel
            method: Delivery method
            properties: Message properties
            body: Message body
        """
        try:
            payload = json.loads(body)
            payload["timestamp"] = payload.get("timestamp", datetime.utcnow().isoformat())
            
            # Store in MongoDB
            EventsDAO.insert(payload)
            
            # Emit via Socket.IO (if callback is set)
            # Remove MongoDB _id before broadcasting (not JSON serializable)
            if hasattr(self, '_socketio_callback') and self._socketio_callback:
                broadcast_payload = {k: v for k, v in payload.items() if k != '_id'}
                self._socketio_callback("device_event", broadcast_payload)
            
            logger.info(
                f"Device event stored: {payload.get('event_type')} for device {payload.get('device_id')}"
            )
        except Exception as e:
            logger.error(f"Device event consumer error: {e}")
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def set_socketio_callback(self, callback):
        """
        Set callback for Socket.IO broadcasting.
        
        Args:
            callback: Function to call with (event_type, data)
        """
        self._socketio_callback = callback

    def start_consuming(self):
        """Start consuming messages from RabbitMQ queues."""
        while self._is_running:
            try:
                params = self._get_connection_params()
                self._connection = pika.BlockingConnection(params)
                self._channel = self._connection.channel()
                
                # Declare exchange and queues
                self._channel.exchange_declare(
                    exchange=MONITORING_EXCHANGE,
                    exchange_type="topic",
                    durable=True
                )
                self._channel.queue_declare(queue=TELEMETRY_QUEUE, durable=True)
                self._channel.queue_declare(queue=DEVICE_EVENTS_QUEUE, durable=True)
                
                # Bind queues to exchange
                self._channel.queue_bind(
                    queue=TELEMETRY_QUEUE,
                    exchange=MONITORING_EXCHANGE,
                    routing_key=TELEMETRY_ROUTING_KEY
                )
                self._channel.queue_bind(
                    queue=DEVICE_EVENTS_QUEUE,
                    exchange=MONITORING_EXCHANGE,
                    routing_key=DEVICE_EVENT_ROUTING_KEY
                )
                
                # Set QoS
                self._channel.basic_qos(prefetch_count=1)
                
                # Start consuming
                self._channel.basic_consume(
                    queue=TELEMETRY_QUEUE,
                    on_message_callback=self._on_telemetry
                )
                self._channel.basic_consume(
                    queue=DEVICE_EVENTS_QUEUE,
                    on_message_callback=self._on_device_event
                )
                
                logger.info("RabbitMQ consumer started")
                self._channel.start_consuming()
                
            except Exception as e:
                logger.error(f"RabbitMQ consumer connection error: {e}")
                if self._connection:
                    try:
                        self._connection.close()
                    except Exception:
                        pass
                # Wait before reconnecting
                import time
                time.sleep(5)

    def start_background(self):
        """Start consumer in background thread."""
        self._is_running = True
        t = threading.Thread(target=self.start_consuming, daemon=True)
        t.start()
        logger.info("RabbitMQ consumer started in background")

    def stop(self):
        """Stop the consumer."""
        self._is_running = False
        if self._channel:
            try:
                self._channel.stop_consuming()
            except Exception:
                pass
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
        logger.info("RabbitMQ consumer stopped")


# Singleton instance
rabbitmq_consumer = RabbitMQConsumer()
