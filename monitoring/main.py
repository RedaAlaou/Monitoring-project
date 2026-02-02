"""
Monitoring Microservice - Main Application Entry Point.
A FastAPI-based microservice for collecting and serving IoT telemetry data.
"""

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import logger
from controllers.telemetry_controller import router as telemetry_router
from controllers.events_controller import router as events_router
from services.rabbitmq_consumer import rabbitmq_consumer
from services.socketio_service import socketio_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting Monitoring Microservice...")
    
    # Start Socket.IO service
    socketio_service.start()
    
    # Set Socket.IO callback for RabbitMQ consumer
    def socketio_emit(event: str, data: dict):
        socketio_service.queue_broadcast(event, data)
    
    rabbitmq_consumer.set_socketio_callback(socketio_emit)
    
    # Start RabbitMQ consumer in background
    rabbitmq_consumer.start_background()
    
    logger.info("Monitoring Microservice started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Monitoring Microservice...")
    rabbitmq_consumer.stop()
    socketio_service.stop()
    logger.info("Monitoring Microservice stopped")


# Create FastAPI application
app = FastAPI(
    title="Monitoring API",
    description="Collects and serves IoT telemetry. Real-time updates via Socket.IO.",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(telemetry_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")

# Mount Socket.IO app for real-time communication
app.mount("/socket.io", socketio_service.socket_app)


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "monitoring"}


# Root endpoint
@app.get("/")
def root():
    """Root endpoint with service information."""
    return {
        "service": "Monitoring Microservice",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "socketio": "/socket.io (WebSocket)"
    }


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("./logs", exist_ok=True)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
    )
