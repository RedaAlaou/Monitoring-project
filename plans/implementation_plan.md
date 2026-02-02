# Step-by-Step Implementation Plan

## Phase 0: Setup (Current State)

### What's Already Done
- ✅ Signing Microservice (backend-api-v1) - Complete
- ✅ PostgreSQL database configured
- ✅ Docker setup ready

### Your Manual Tasks
- [ ] Ensure Docker Desktop is installed and running
- [ ] Ensure Kubernetes (microk8s) is installed (optional for now)
- [ ] Create project structure folders

---

## Phase 1: Device Management Microservice (Basic)

### Step 1.1: Create Project Structure
```
device-management/
├── main.py
├── controllers/
│   └── __init__.py
├── dal/
│   └── __init__.py
├── dto/
│   └── __init__.py
├── entities/
│   └── __init__.py
├── services/
│   └── __init__.py
├── helpers/
│   └── __init__.py
├── docker/
│   └── Dockerfile
├── k8s/
│   └── deployment.yaml
├── requirements.txt
└── docker-compose.yml
```

**Manual Task:** Create these folders manually

---

### Step 1.2: Setup Configuration (helpers/config.py)

**Files to create:**
- `device-management/helpers/config.py`

**Manual Task:**
- Create `.env` file with:
  ```
  SERVER_DB=localhost
  NAME_DB=db_device_management
  USER_DB=admin
  PASSWORD_DB=1234
  REDIS_HOST=localhost
  ```

---

### Step 1.3: Create Database Entities

**Files to create:**
- `device-management/entities/device.py`
- `device-management/entities/__init__.py`

**This does:**
- Defines `t_devices` table with status enum

**Manual Task:**
- Nothing - code does it all

---

### Step 1.4: Create DTOs

**Files to create:**
- `device-management/dto/device_dto.py`
- `device-management/dto/__init__.py`

**This does:**
- Request/Response models for API validation

---

### Step 1.5: Create DAL (Data Access Layer)

**Files to create:**
- `device-management/dal/device_dao.py`
- `device-management/dal/__init__.py`

**This does:**
- CRUD operations for devices

---

### Step 1.6: Create Controllers

**Files to create:**
- `device-management/controllers/device_controller.py`
- `device-management/controllers/__init__.py`

**This does:**
- API endpoints:
  - GET `/devices/` - List all
  - POST `/devices/` - Create
  - GET `/devices/{id}` - Get one
  - PUT `/devices/{id}` - Update
  - DELETE `/devices/{id}` - Delete

---

### Step 1.7: Create Main Application

**Files to create:**
- `device-management/main.py`

**This does:**
- FastAPI app initialization
- Include routers

---

### Step 1.8: Docker Setup

**Files to create:**
- `device-management/requirements.txt`
- `device-management/docker/Dockerfile`

**Manual Task:**
- Build and run:
  ```bash
  cd device-management/docker
  docker build -t device-management:1.0 .
  docker run -p 8001:8000 device-management:1.0
  ```

---

### Phase 1 Summary
✅ Device Management Microservice running on port 8001
✅ CRUD operations for devices
✅ Database integration

---

## Phase 2: Device Status & Lifecycle

### Step 2.1: Add Status Management to Controller

**Files to modify:**
- `device-management/controllers/device_controller.py`

**New endpoints:**
- PUT `/devices/{id}/status` - Update device status
- GET `/devices/in_stock` - Filter by in_stock
- GET `/devices/deployed` - Filter by deployed

---

### Step 2.2: Add Device Logs

**Files to create:**
- `device-management/entities/device_log.py`
- `device-management/dal/device_log_dao.py`
- `device-management/services/device_service.py`

**This does:**
- Track all device status changes (audit log)

---

### Step 2.3: Add Deploy/Recall Actions

**Files to modify:**
- `device-management/controllers/device_controller.py`

**New endpoints:**
- PUT `/devices/{id}/deploy` - Deploy to field
- PUT `/devices/{id}/recall` - Recall to stock
- PUT `/devices/{id}/maintenance` - Send to maintenance

**Manual Task:**
- Test with:
  ```bash
  # Deploy a device
  curl -X PUT http://localhost:8001/devices/1/deploy
  
  # Recall a device
  curl -X PUT http://localhost:8001/devices/1/recall
  ```

---

## Phase 3: Redis Integration

### Step 3.1: Add Redis Config

**Files to modify:**
- `device-management/helpers/config.py`

**Manual Task:**
- Ensure Redis is running on port 6379

---

### Step 3.2: Add Caching

**Files to create:**
- `device-management/services/cache_service.py`

**This does:**
- Cache device list
- Invalidate cache on changes

---

## Phase 4: Monitoring Microservice

### Step 4.1: Create Project Structure

```
monitoring/
├── main.py
├── controllers/
├── dal/
├── dto/
├── entities/
├── services/
├── helpers/
├── docker/
├── k8s/
└── requirements.txt
```

**Manual Task:** Create folders

---

### Step 4.2: MongoDB Setup

**Files to create:**
- `monitoring/helpers/config.py`

**Manual Task:**
- Create `.env`:
  ```
  MONGO_HOST=localhost
  MONGO_PORT=27017
  MONGO_DB=db_monitoring
  ```

---

### Step 4.3: Create MongoDB Entities

**Files to create:**
- `monitoring/entities/monitoring_data.py`

**This does:**
- MongoDB collections for device data

---

### Step 4.4: Create RabbitMQ Consumer

**Files to create:**
- `monitoring/services/rabbitmq_consumer.py`

**This does:**
- Listen to device data queue
- Store in MongoDB

**Manual Task:**
- Ensure RabbitMQ is running on port 5672

---

### Step 4.5: Create API Endpoints

**Files to create:**
- `monitoring/controllers/monitoring_controller.py`

**Endpoints:**
- GET `/monitoring/data` - Get data
- GET `/monitoring/stats` - Get stats

---

### Step 4.6: Add Socket.IO

**Files to create:**
- `monitoring/services/socket_service.py`
- Modify `monitoring/main.py`

**This does:**
- Real-time data broadcasting

---

## Phase 5: Integration

### Step 5.1: Update Device Management to Publish Events

**Files to modify:**
- `device-management/services/device_service.py`

**This does:**
- Publish device events to RabbitMQ

---

### Step 5.2: Update Docker Compose

**Files to create:**
- `docker-compose.yml` at project root

**Manual Task:**
- Run all services:
  ```bash
  docker-compose up -d
  ```

---

## Phase 6: Kubernetes Deployment (Optional)

### Step 6.1: Create K8s Manifests

**Files to create:**
- `device-management/k8s/deployment.yaml`
- `device-management/k8s/service.yaml`
- `monitoring/k8s/deployment.yaml`
- `monitoring/k8s/service.yaml`

**Manual Task:**
- Deploy to Kubernetes:
  ```bash
  kubectl apply -f device-management/k8s/
  kubectl apply -f monitoring/k8s/
  ```

---

## Complete Checklist

### Manual Tasks Summary

| Phase | Task | Description |
|-------|------|-------------|
| 0 | Install Docker | Ensure Docker Desktop running |
| 0 | Install K8s | Install microk8s (optional) |
| 1 | Create folders | Create device-management structure |
| 1 | Create .env | Database config file |
| 1 | Build Docker | `docker build` and `docker run` |
| 2 | Test API | Use curl or Postman to test |
| 3 | Start Redis | Ensure Redis running |
| 4 | Create folders | Create monitoring structure |
| 4 | Create .env | MongoDB config file |
| 4 | Start RabbitMQ | Ensure RabbitMQ running |
| 5 | Run Compose | `docker-compose up -d` |
| 6 | Deploy K8s | `kubectl apply` commands |

### Automated Tasks (I Will Do)

- All Python files (entities, DTOs, DAL, controllers, services)
- Dockerfiles and requirements.txt
- K8s manifests
- Main application files

---

## Estimated Timeline

| Phase | Effort | Description |
|-------|--------|-------------|
| Phase 1 | 2-3 hours | Basic CRUD + Docker |
| Phase 2 | 1-2 hours | Status lifecycle |
| Phase 3 | 1 hour | Redis caching |
| Phase 4 | 3-4 hours | Monitoring + MongoDB + RabbitMQ + Socket.IO |
| Phase 5 | 1 hour | Integration |
| Phase 6 | 1-2 hours | K8s deployment |

**Total: ~10-13 hours**

---

## Next Step

Shall I start with **Phase 1: Device Management Microservice (Basic)**?
I'll create all the files step by step, and you'll run the manual tasks as we go.
