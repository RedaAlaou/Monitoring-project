# Device Management Microservice

A FastAPI-based microservice for managing IoT devices - inventory, deployment, and lifecycle tracking.

## Features

- **Device Registry**: Register and manage IoT devices
- **Inventory Tracking**: Track device status (in_stock, deployed, maintenance, etc.)
- **Deployment Management**: Deploy devices to field and recall them
- **Lifecycle Logging**: Track all device status changes

## API Endpoints

### Device CRUD Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/devices/` | List all devices (with pagination) |
| GET | `/api/v1/devices/in_stock` | List in-stock devices |
| GET | `/api/v1/devices/deployed` | List deployed devices |
| GET | `/api/v1/devices/maintenance` | List devices in maintenance |
| GET | `/api/v1/devices/{id}` | Get device by ID |
| POST | `/api/v1/devices/` | Create new device |
| PUT | `/api/v1/devices/{id}` | Update device |
| DELETE | `/api/v1/devices/{id}` | Retire device |

### Status Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/api/v1/devices/{id}/status` | Update device status |
| PUT | `/api/v1/devices/{id}/deploy` | Deploy device to field |
| PUT | `/api/v1/devices/{id}/recall` | Recall device to stock |
| PUT | `/api/v1/devices/{id}/maintenance` | Send to maintenance |

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (create `.env`):
```env
SERVER_DB=localhost
NAME_DB=db_device_management
USER_DB=admin
PASSWORD_DB=1234
```

3. Run the application:
```bash
python main.py
```

4. Access API documentation:
```
http://localhost:8001/docs
```

### Docker

1. Build and run:
```bash
cd docker
docker-compose up -d
```

2. Access the service at `http://localhost:8001`

### Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

## Device Status Flow

```
[in_stock] ─► [reserved] ─► [deployed] ─► [maintenance] ─► [retired]
    │              │             │               │
    │              │             │               │
    └──────────────┴─────────────┴───────────────┘
```

## Project Structure

```
device-management/
├── main.py                 # Application entry point
├── controllers/
│   └── device_controller.py # API endpoints
├── dal/
│   └── device_dao.py       # Database operations
├── dto/
│   └── device_dto.py       # Request/Response models
├── entities/
│   └── device.py           # SQLAlchemy models
├── helpers/
│   └── config.py           # Configuration
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── k8s/
│   └── deployment.yaml
├── requirements.txt
└── README.md
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SERVER_DB | localhost | PostgreSQL server host |
| NAME_DB | db_device_management | Database name |
| USER_DB | admin | Database user |
| PASSWORD_DB | 1234 | Database password |

## Dependencies

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Uvicorn
