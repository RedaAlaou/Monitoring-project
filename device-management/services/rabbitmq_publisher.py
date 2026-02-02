"""
RabbitMQ Publisher Service for Device Management.
Publishes device events to RabbitMQ for the Monitoring service.
"""

import json
import pika
import threading
from typing import Optional, Dict, Any
from datetime import datetime
from helpers.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, logger


class RabbitMQPublisher:
    """RabbitMQ publisher for device events."""

    def __init__(self):
        """Initialize RabbitMQ connection."""
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None
        self._lock = threading.Lock()

    @property
    def connection(self) -> pika.BlockingConnection:
        """Lazy initialization of RabbitMQ connection."""
        # Ensure connection creation is also locked or handle it within publish
        if self._connection is None or self._connection.is_closed:
            try:
                credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
                parameters = pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                    socket_timeout=5
                )
                self._connection = pika.BlockingConnection(parameters)
                self._channel = self._connection.channel()
                
                # Declare exchange
                self._channel.exchange_declare(
                    exchange='device_events',
                    exchange_type='topic',
                    durable=True
                )
                
                logger.info(f"RabbitMQ connected: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
            except pika.exceptions.AMQPConnectionError as e:
                logger.error(f"RabbitMQ connection failed: {e}")
                raise
        return self._connection

    @property
    def channel(self) -> pika.channel.Channel:
        """Get RabbitMQ channel."""
        if self._channel is None or self._channel.is_closed:
            self.connection  # This will create the connection
            self._channel = self._connection.channel()
        return self._channel

    def publish_event(self, routing_key: str, event_data: Dict[str, Any]) -> bool:
        """
        Publish an event to RabbitMQ.
        
        Args:
            routing_key: The routing key for the message (e.g., 'device.telemetry', 'device.event')
            event_data: The event data to publish
            
        Returns:
            True if published successfully, False otherwise
        """
        with self._lock:
            try:
                # Add timestamp if not present
                if 'timestamp' not in event_data:
                    event_data['timestamp'] = datetime.utcnow().isoformat()
                
                message = json.dumps(event_data)
                
                self.channel.basic_publish(
                    exchange='device_events',
                    routing_key=routing_key,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Persistent message
                        content_type='application/json'
                    )
                )
                
                logger.info(f"Published event: {routing_key}")
                return True
                
            except (pika.exceptions.AMQPConnectionError, pika.exceptions.AMQPChannelError) as e:
                logger.error(f"RabbitMQ publish error: {e}")
                self._connection = None  # Reset connection
                self._channel = None
                return False
            except Exception as e:
                logger.error(f"Unexpected RabbitMQ error: {e}")
                return False

    def publish_telemetry(self, device_id: int, device_name: str, data: Dict[str, Any]) -> bool:
        """
        Publish device telemetry data.
        
        Args:
            device_id: The device ID
            device_name: The device name
            data: Telemetry data
            
        Returns:
            True if published successfully
        """
        event_data = {
            'event_type': 'telemetry',
            'device_id': device_id,
            'device_name': device_name,
            'data': data
        }
        return self.publish_event('device.telemetry', event_data)

    def publish_device_event(self, device_id: int, device_name: str, event_type: str, details: Dict[str, Any]) -> bool:
        """
        Publish device event (deployment, recall, maintenance, etc.).
        
        Args:
            device_id: The device ID
            device_name: The device name
            event_type: Type of event (deployed, recalled, maintenance, etc.)
            details: Event details
            
        Returns:
            True if published successfully
        """
        event_data = {
            'event_type': event_type,
            'device_id': device_id,
            'device_name': device_name,
            'details': details
        }
        return self.publish_event('device.event', event_data)

    def publish_status_change(self, device_id: int, device_name: str, old_status: str, new_status: str, location: str = None) -> bool:
        """
        Publish device status change event.
        
        Args:
            device_id: The device ID
            device_name: The device name
            old_status: Previous status
            new_status: New status
            location: Optional location
            
        Returns:
            True if published successfully
        """
        details = {
            'old_status': old_status,
            'new_status': new_status,
            'location': location
        }
        return self.publish_device_event(device_id, device_name, 'status_change', details)

    def close(self):
        """Close RabbitMQ connection."""
        try:
            if self._connection and not self._connection.is_closed:
                self._connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")


# Singleton instance
rabbitmq_publisher = RabbitMQPublisher()
