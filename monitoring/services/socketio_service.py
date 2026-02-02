"""
Socket.IO Service for Monitoring microservice.
Handles real-time broadcasting to connected clients.
"""

import asyncio
import socketio
from typing import Optional
from config.settings import SOCKETIO_CORS_ORIGINS, logger


class SocketIOService:
    """Socket.IO service for real-time communication."""

    def __init__(self):
        """Initialize Socket.IO server."""
        self._sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins=SOCKETIO_CORS_ORIGINS
        )
        self._socket_app = socketio.ASGIApp(self._sio)
        self._broadcast_queue: asyncio.Queue = asyncio.Queue()
        self._broadcast_task: Optional[asyncio.Task] = None
        
        # Register Socket.IO events
        self._register_events()

    def _register_events(self):
        """Register Socket.IO event handlers."""
        @self._sio.event
        async def connect(sid, environ, auth):
            logger.info(f"Socket.IO client connected: {sid}")

        @self._sio.event
        def disconnect(sid):
            logger.info(f"Socket.IO client disconnected: {sid}")

    @property
    def sio(self) -> socketio.AsyncServer:
        """Get Socket.IO server instance."""
        return self._sio

    @property
    def socket_app(self):
        """Get ASGI app for Socket.IO."""
        return self._socket_app

    async def _broadcast_loop(self):
        """Background task to broadcast messages from queue."""
        logger.info("Socket.IO broadcast loop started")
        while True:
            try:
                event, data = await self._broadcast_queue.get()
                logger.info(f"Broadcasting {event} event to all clients")
                await self._sio.emit(event, data)
                logger.info(f"Successfully broadcasted {event}")
            except asyncio.CancelledError:
                logger.info("Broadcast loop cancelled")
                break
            except Exception as e:
                logger.error(f"Socket.IO broadcast error: {e}")

    def start(self):
        """Start the Socket.IO broadcast loop."""
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())
        logger.info("Socket.IO service started")

    def stop(self):
        """Stop the Socket.IO broadcast loop."""
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self._broadcast_task)
            except (asyncio.CancelledError, RuntimeError):
                pass
        logger.info("Socket.IO service stopped")

    def queue_broadcast(self, event: str, data: dict):
        """
        Queue a message for broadcasting.
        
        Args:
            event: Event name
            data: Event data
        """
        try:
            logger.info(f"Queueing {event} event for broadcast: device_id={data.get('device_id')}")
            self._broadcast_queue.put_nowait((event, data))
        except Exception as e:
            logger.error(f"Error queueing broadcast: {e}")

    async def broadcast(self, event: str, data: dict):
        """
        Broadcast a message immediately.
        
        Args:
            event: Event name
            data: Event data
        """
        await self._sio.emit(event, data, broadcast=True)


# Initialize Socket.IO service
socketio_service = SocketIOService()
