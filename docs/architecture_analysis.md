# Cloud Native Monitoring App - Architecture Analysis & Implementation Plan

## 1. Current Architecture Analysis (backend-api-v1 - Signing Microservice)

### 1.1 Architecture Pattern: Layered Architecture (MVC-inspired)

The existing codebase follows a **Layered Architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                      CONTROLLERS                                 │
│              (auth_controller.py)                               │
│         Handles HTTP requests/responses                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DAL (Data Access Layer)                  │
│           (user_dao.py, black_listed_dao.py)                    │
│         Database operations abstraction                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ENTITIES                                  │
│                   (user.py)                                     │
│              SQLAlchemy ORM models                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                    PostgreSQL Database
```

### 1.2 Directory Structure

```
backend-api-v1/
├── main.py                 # Application entry point
├── controllers/
│   └── auth_controller.py  # HTTP route handlers
├── dal/
│   ├── user_dao.py         # User database operations
│   └── black_listed_dao.py # Token blacklist operations
├── dto/
│   └── users_dto.py        # Request/Response DTOs
├── entities/
│   └── user.py             # SQLAlchemy ORM entities
├── helpers/
│   ├── config.py           # Configuration & DB setup
│   └── utils.py            # JWT & Password utilities
├── test/
│   └── api_test.http       # HTTP test file
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Container image
├── init.sql                # DB initialization
└── requirements.txt        # Python dependencies
```

### 1.3 Key Technologies Used

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Authentication | JWT (python-jose) |
| Password Hashing | Argon2 (argon2-cffi) |
| Validation | Pydantic |
| Containerization | Docker |
| Logging | Python logging |

### 1.4 API Endpoints (Signing Microservice)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/users/add` | Register new user | No |
| POST | `/users/auth` | Authenticate user | No |
| POST | `/users/verify-token` | Verify JWT token | No |
| GET | `/users/` | Get all users | Yes |
| POST | `/users/logout` | Logout user | Yes |

### 1.5 Database Schema

**t_users table:**
- `id` (Integer, PK, Auto-increment)
- `email` (String, Unique, Indexed)
- `password` (String, 128 chars, Hashed)
- `is_admin` (Boolean, Default: False)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**t_blacklist_tokens table:**
- `id` (Integer, PK, Auto-increment)
- `token` (String, 500 chars, Unique)
- `blacklisted_on` (DateTime)

---

## 2. Project Requirements Summary

### 2.1 Three Microservices Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        API Gateway (nginx)                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│    Signing    │    │    Device     │    │   Monitoring  │
│  Microservice │◄──►│  Management   │◄──►│  Microservice │
│   (PostgreSQL │    │  Microservice │    │    (MongoDB)  │
│    Redis)     │    │  (PostgreSQL  │    │   Socket.IO)  │
│               │    │    Redis)     │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌─────────────┐     ┌─────────────┐
            │   RabbitMQ  │     │  Front-end  │
            │  (Messages) │     │  (Socket.IO │
            └─────────────┘     └─────────────┘
```

### 2.2 Communication Patterns

| Services | Communication Type | Protocol |
|----------|-------------------|----------|
| Signing ↔ Device Management | Synchronous | HTTP REST |
| Device Management ↔ Monitoring | Asynchronous | RabbitMQ |
| Monitoring ↔ Frontend | Real-time | Socket.IO |

### 2.3 Technology Stack

| Layer | Technologies |
|-------|-------------|
| Microservices Framework | FastAPI |
| Relational DB | PostgreSQL |
| Cache/Session | Redis |
| Document DB | MongoDB |
| Message Broker | RabbitMQ |
| Real-time | Socket.IO |
| Containerization | Docker |
| Orchestration | Kubernetes (microk8s) |
| API Gateway | nginx |
| Monitoring | Prometheus + Grafana |
| Code Quality | SonarQube |

---

## 3. Implementation Plan

### 3.1 Signing Microservice (backend-api-v1) - ✅ ALREADY DONE

### 3.2 Device Management Microservice - TO BE IMPLEMENTED

**Features:**
- Device registration
- Device configuration
- Device status management
- Publish device events to RabbitMQ

**Architecture:**
```
device-management/
├── main.py
├── controllers/
│   └── device_controller.py
├── dal/
│   ├── device_dao.py
│   └── __init__.py
├── dto/
│   └── device_dto.py
├── entities/
│   └── device.py
├── business/
│   └── device_service.py
├── helpers/
│   ├── config.py
│   ├── rabbitmq_client.py
│   └── utils.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── k8s/
    ├── deployment.yaml
    ├── service.yaml
    └── configmap.yaml
```

**API Endpoints:**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/devices/` | Register device | Yes |
| GET | `/devices/` | List all devices | Yes |
| GET | `/devices/{id}` | Get device by ID | Yes |
| PUT | `/devices/{id}` | Update device | Yes |
| DELETE | `/devices/{id}` | Delete device | Yes |
| GET | `/devices/{id}/status` | Get device status | Yes |
| POST | `/devices/{id}/events` | Publish event to RabbitMQ | Yes |

**Database Schema (PostgreSQL):**
- `t_devices`: id, name, type, config (JSON), status, owner_id, created_at, updated_at
- `t_device_events`: id, device_id, event_type, payload, timestamp

### 3.3 Monitoring Microservice - TO BE IMPLEMENTED

**Features:**
- Listen to RabbitMQ for data ingestion
- Store IoT data in MongoDB
- Provide APIs for querying device data
- Real-time updates via Socket.IO

**Architecture:**
```
monitoring/
├── main.py
├── controllers/
│   ├── monitoring_controller.py
│   └── socket_controller.py
├── dal/
│   ├── monitoring_dao.py
│   └── __init__.py
├── dto/
│   └── monitoring_dto.py
├── entities/
│   └── monitoring_data.py
├── services/
│   ├── rabbitmq_consumer.py
│   ├── socket_service.py
│   └── data_processor.py
├── helpers/
│   ├── config.py
│   └── utils.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── k8s/
    ├── deployment.yaml
    ├── service.yaml
    └── configmap.yaml
```

**API Endpoints:**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/monitoring/data` | Get monitoring data | Yes |
| GET | `/monitoring/data/{device_id}` | Get device data | Yes |
| GET | `/monitoring/stats` | Get statistics | Yes |
| WS | `/ws/monitoring` | Socket.IO real-time | Yes |

**MongoDB Collections:**
- `monitoring_data`: device_id, timestamp, metrics, raw_data
- `device_alerts`: device_id, alert_type, message, timestamp, acknowledged

### 3.4 IoT Device Simulator - TO BE IMPLEMENTED

**Features:**
- Simulate IoT device data
- Publish data via MQTT/HTTP
- Custom Python scripts

**Architecture:**
```
iot-devices/
├── main.py
├── device_simulator.py
├── mqtt_publisher.py
├── http_publisher.py
├── config/
│   └── devices.yaml
├── docker/
│   └── Dockerfile
└── requirements.txt
```

---

## 4. Deployment Architecture

### 4.1 Docker Compose (Development)

```yaml
services:
  # Existing services
  backend:
    build: ./backend-api-v1
    # ... existing config

  # New services
  device-management:
    build: ./device-management
    depends_on:
      - db
      - redis
      - rabbitmq
    environment:
      - SERVER_DB=db
      - REDIS_HOST=redis
      - RABBITMQ_HOST=rabbitmq

  monitoring:
    build: ./monitoring
    depends_on:
      - mongodb
      - rabbitmq
    environment:
      - MONGO_HOST=mongodb
      - RABBITMQ_HOST=rabbitmq

  # Infrastructure
  db:
    image: postgres:alpine
    # ... existing config

  redis:
    image: redis:alpine
    ports:
      - 6379:6379

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - 5672:5672
      - 15672:15672

  mongodb:
    image: mongo:alpine
    ports:
      - 27017:27017
    volumes:
      - mongo_data:/data/db

  nginx:
    image: nginx:alpine
    ports:
      - 80:80
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - device-management
      - monitoring

volumes:
  mongo_data:
```

### 4.2 Kubernetes Deployment (Production)

Each microservice will have:
- Deployment with replica sets
- Service (ClusterIP/NodePort)
- ConfigMap for configuration
- Secret for sensitive data
- Horizontal Pod Autoscaler (optional)

---

## 5. Next Steps

1. **Review this plan** and confirm understanding
2. **Create Device Management Microservice** following the same architecture pattern
3. **Create Monitoring Microservice** with MongoDB and Socket.IO
4. **Create IoT Device Simulator**
5. **Set up Docker Compose** for local testing
6. **Configure Kubernetes** deployment files
7. **Implement monitoring** with Prometheus/Grafana
8. **Deploy to cloud** (AWS/Azure/GCP)
