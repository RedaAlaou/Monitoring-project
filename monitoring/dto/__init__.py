"""DTO (Data Transfer Objects) package for Monitoring microservice."""
from dto.telemetry_dto import TelemetryResponse
from dto.events_dto import EventResponse

__all__ = ["TelemetryResponse", "EventResponse"]
