"""
Device Management Microservice - Main Application Entry Point.
A FastAPI-based microservice for managing IoT devices.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.device_controller import router as device_router
from helpers.config import Base, engine, logger

# Create FastAPI application
app = FastAPI(
    title="Device Management Microservice",
    description="Microservice for managing IoT devices - inventory, deployment, and lifecycle tracking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include device management routes
app.include_router(device_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    logger.info("Starting Device Management Microservice...")
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "device-management"}


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Device Management Microservice",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
