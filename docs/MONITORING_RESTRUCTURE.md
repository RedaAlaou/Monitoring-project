# Monitoring Service - Restructuring Plan

## Current Problems

The current [`monitoring/app.py`](monitoring/app.py) file has **all code mixed together**:
- ❌ No separation of concerns
- ❌ No controllers folder
- ❌ No DAL folder for MongoDB operations
- ❌ No DTOs folder for request/response models
- ❌ No entities folder for data models
- ❌ No services folder for business logic
- ❌ No helpers folder for utilities
- ❌ 311 lines in single file (too long)

## Current File Structure

```
monitoring/
├── app.py                    # 311 lines - EVERYTHING mixed here!
├── requirements.txt
├── config/
│   └── settings.py
├── dockers/
│   └── Dockerfile
└── k8s/
    └── deployment.yaml
```

## Proposed Restructured File Structure

```
monitoring/
├── main.py                   # Application entry point (clean)
├── requirements.txt
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration only
├── controllers/
│   ├── __init__.py
│   ├── telemetry_controller.py   # Telemetry endpoints
│   └── events_controller.py      # Events endpoints
├── dal/
│   ├── __init__.py
│   ├── mongo_client.py           # MongoDB connection
│   ├── telemetry_dao.py          # Telemetry CRUD
│   └── events_dao.py             # Events CRUD
├── dto/
│   ├── __init__.py
│   ├── telemetry_dto.py          # Telemetry request/response
│   └── events_dto.py             # Events request/response
├── services/
│   ├── __init__.py
│   ├── rabbitmq_consumer.py      # RabbitMQ consumer logic
│   └── socketio_service.py       # Socket.IO broadcasting
├── helpers/
│   ├── __init__.py
│   └── utils.py                  # Utility functions
├── dockers/
│   └── Dockerfile
├── k8s/
│   └── deployment.yaml
└── logs/
    └── monitoring.log
```

## Code Splitting Details

### 1. Main Entry Point ([`main.py`](monitoring/main.py))
```python
# Only initialization and routing
from fastapi import FastAPI
from controllers.telemetry_controller import router as telemetry_router
from controllers.events_controller import router as events_router
from config.settings import logger

app = FastAPI(title="Monitoring API", version="1.0.0")
app.include_router(telemetry_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
```

### 2. Controllers Layer

**[`controllers/telemetry_controller.py`](monitoring/controllers/telemetry_controller.py)**
```python
# Only HTTP endpoint handling
router = APIRouter(prefix="/telemetry", tags=["telemetry"])

@router.get("/")
def get_telemetry(device_id: int = None, limit: int = 100):
    return telemetry_dao.get_all(device_id=device_id, limit=limit)
```

**[`controllers/events_controller.py`](monitoring/controllers/events_controller.py)**
```python
# Only HTTP endpoint handling
router = APIRouter(prefix="/events", tags=["events"])

@router.get("/")
def get_events(device_id: int = None, event_type: str = None):
    return events_dao.get_all(device_id=device_id, event_type=event_type)
```

### 3. DAL Layer (MongoDB)

**[`dal/telemetry_dao.py`](monitoring/dal/telemetry_dao.py)**
```python
# Only database operations
class TelemetryDAO:
    @staticmethod
    def get_all(device_id: int = None, limit: int = 100):
        # MongoDB query logic here
    
    @staticmethod
    def insert(data: dict):
        # Insert logic here
    
    @staticmethod
    def count():
        # Count logic here
```

**[`dal/events_dao.py`](monitoring/dal/events_dao.py)**
```python
# Only database operations
class EventsDAO:
    @staticmethod
    def get_all(device_id: int = None, event_type: str = None):
        # MongoDB query logic here
```

### 4. DTO Layer

**[`dto/telemetry_dto.py`](monitoring/dto/telemetry_dto.py)**
```python
class TelemetryRequest(BaseModel):
    device_id: int
    device_type: str
    timestamp: str
    data: dict

class TelemetryResponse(BaseModel):
    id: str
    device_id: int
    device_type: str
    timestamp: str
    data: dict
```

**[`dto/events_dto.py`](monitoring/dto/events_dto.py)**
```python
class EventRequest(BaseModel):
    device_id: int
    event_type: str
    timestamp: str
    details: dict

class EventResponse(BaseModel):
    id: str
    device_id: int
    event_type: str
    timestamp: str
    details: dict
```

### 5. Services Layer

**[`services/rabbitmq_consumer.py`](monitoring/services/rabbitmq_consumer.py)**
```python
# Only RabbitMQ consumption logic
def on_telemetry(channel, method, properties, body):
    # Process telemetry message
    pass

def on_device_event(channel, method, properties, body):
    # Process event message
    pass
```

**[`services/socketio_service.py`](monitoring/services/socketio_service.py)**
```python
# Only Socket.IO broadcasting
async def broadcast_telemetry(data: dict):
    await sio.emit("telemetry", data)

async def broadcast_event(data: dict):
    await sio.emit("device_event", data)
```

### 6. Helpers Layer

**[`helpers/utils.py`](monitoring/helpers/utils.py)**
```python
# Utility functions
def format_timestamp(timestamp: str) -> str:
    pass

def validate_device_data(data: dict) -> bool:
    pass
```

## Comparison Table

| Aspect | Current (app.py) | After Restructure |
|--------|-----------------|-------------------|
| Lines per file | 311 | ~50-80 per file |
| Separation of concerns | ❌ No | ✅ Yes |
| Testability | ❌ Hard | ✅ Easy |
| Maintainability | ❌ Poor | ✅ Good |
| Reusability | ❌ No | ✅ Yes |
| Follows project pattern | ❌ No | ✅ Yes |

## Implementation Steps

1. Create new folder structure
2. Move MongoDB connection to `dal/mongo_client.py`
3. Move telemetry endpoints to `controllers/telemetry_controller.py`
4. Move events endpoints to `controllers/events_controller.py`
5. Move DTOs to `dto/` folder
6. Move RabbitMQ consumer to `services/rabbitmq_consumer.py`
7. Move Socket.IO logic to `services/socketio_service.py`
8. Clean up `main.py` to only initialize app
9. Add proper `__init__.py` files
10. Add logging setup to `main.py`

## Files to Create/Modify

### New Files to Create:
- `main.py`
- `controllers/__init__.py`
- `controllers/telemetry_controller.py`
- `controllers/events_controller.py`
- `dal/__init__.py`
- `dal/mongo_client.py`
- `dal/telemetry_dao.py`
- `dal/events_dao.py`
- `dto/__init__.py`
- `dto/telemetry_dto.py`
- `dto/events_dto.py`
- `services/__init__.py`
- `services/rabbitmq_consumer.py`
- `services/socketio_service.py`
- `helpers/__init__.py`
- `helpers/utils.py`

### Files to Delete:
- `app.py` (replaced by restructured code)

## Benefits of Restructuring

1. **Clean Code** - Each file has a single responsibility
2. **Easy Testing** - Can test controllers, DAO, services independently
3. **Easy Maintenance** - Changes in one layer don't affect others
4. **Follows Project Pattern** - Matches device-management structure
5. **Scalable** - Easy to add new features
6. **Team Collaboration** - Multiple developers can work on different layers

## Status

| Task | Status |
|------|--------|
| Plan creation | ✅ Done |
| User approval | ⏳ Pending |
| Implementation | ❌ Not started |
