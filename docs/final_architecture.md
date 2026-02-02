# Final Architecture: IoT Device Monitoring + Internal Inventory Management

## Core Concept

**Primary Purpose:** Monitor IoT devices in the field
**Secondary Feature:** Internal inventory tracking (available in stock vs deployed)

This is like Samsung's internal system where they:
- Monitor millions of deployed devices (temperature, status, health)
- Know which spare devices are available in their warehouses
- Track devices being prepared for deployment

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API Gateway (nginx)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│     Signing       │    │   Device Store    │    │    Monitoring     │
│   Microservice    │    │   Microservice    │    │   Microservice    │
│  (PostgreSQL)     │    │  (PostgreSQL)     │    │   (MongoDB)       │
│                   │    │                   │    │                   │
│ - User Auth       │    │ - Device Registry │    │ - Data Ingestion  │
│ - Admin Roles     │    │ - Stock Tracking  │    │ - Real-time Data  │
│ - JWT Tokens      │    │ - Deploy Status   │    │ - Alerts          │
└───────────────────┘    └───────────────────┘    └───────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
            ┌─────────────┐                 ┌─────────────┐
            │   RabbitMQ  │                 │   Frontend  │
            │  (Events)   │                 │  (Socket.IO │
            └─────────────┘                 └─────────────┘
```

---

## Device Management Microservice (Enhanced)

### Core Features (From PDF + Enhancement)

**1. Device Registry (From PDF)**
- Register new devices
- Configure device settings
- Track device status

**2. Stock Tracking (Your Enhancement)**
- Know which devices are in stock (spare/backup)
- Know which devices are deployed (in the field)
- Know which devices are in maintenance

**3. Deployment Management**
- Deploy devices from stock to field
- Recall devices from field to stock
- Track deployment locations

### Device Status Enum

| Status | Description | Location |
|--------|-------------|----------|
| `in_stock` | Available in warehouse | Warehouse |
| `reserved` | Reserved for future deployment | Warehouse |
| `deployed` | Active in the field | Field |
| `maintenance` | Under repair/maintenance | Workshop |
| `retired` | No longer usable | Archived |

### Device Lifecycle

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ in_stock │────►│ reserved │────►│ deployed │────►│ retired  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
      │                                 │
      │                                 │
      ▼                                 ▼
┌──────────┐                      ┌──────────┐
│maintenance│◄─────────────────────│  back to │
└──────────┘                      │  stock   │
                                  └──────────┘
```

---

## Monitoring Microservice (From PDF)

### Core Features (From PDF)

**1. Data Ingestion**
- Collect data from deployed devices
- Store in MongoDB
- Process in real-time

**2. Real-time Monitoring**
- Device health (online/offline)
- Metrics (temperature, CPU, memory)
- Socket.IO for live updates

**3. Alerts**
- Abnormal readings
- Device offline alerts
- Threshold violations

---

## Database Schema

### Device Store (PostgreSQL)

**t_devices:**
```sql
id              INT PRIMARY KEY AUTOINCREMENT
name            VARCHAR(100) NOT NULL
type            VARCHAR(50) NOT NULL          -- sensor, gateway, etc.
serial_number   VARCHAR(100) UNIQUE
status          VARCHAR(20) DEFAULT 'in_stock' -- in_stock, reserved, deployed, maintenance, retired
location        VARCHAR(100)                   -- warehouse name or deployment location
specs           JSONB                          -- device specifications
purchase_date   DATE
deploy_date     DATE
last_maintenance DATE
created_at      TIMESTAMP DEFAULT NOW()
updated_at      TIMESTAMP DEFAULT NOW()
```

**t_device_logs:**
```sql
id              INT PRIMARY KEY AUTOINCREMENT
device_id       INT REFERENCES t_devices(id)
action          VARCHAR(50)                    -- deployed, recalled, maintained
old_status      VARCHAR(20)
new_status      VARCHAR(20)
performed_by    INT REFERENCES t_users(id)
notes           TEXT
created_at      TIMESTAMP DEFAULT NOW()
```

---

## API Endpoints

### Device Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/devices/` | List all devices (with status filter) |
| POST | `/devices/` | Register new device |
| GET | `/devices/{id}` | Get device details |
| PUT | `/devices/{id}` | Update device |
| DELETE | `/devices/{id}` | Retire device |
| GET | `/devices/in_stock` | List available devices |
| GET | `/devices/deployed` | List deployed devices |
| PUT | `/devices/{id}/deploy` | Deploy device to field |
| PUT | `/devices/{id}/recall` | Recall device to stock |
| PUT | `/devices/{id}/maintenance` | Send to maintenance |

### Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/monitoring/data` | Get device monitoring data |
| GET | `/monitoring/data/{device_id}` | Get specific device data |
| GET | `/monitoring/stats` | Get aggregate statistics |
| GET | `/monitoring/alerts` | Get active alerts |
| WS | `/ws/monitoring` | Real-time Socket.IO |

---

## Data Flow

### Device Deployment Flow
```
1. Admin checks in_stock devices
   GET /devices/in_stock

2. Admin deploys device to field
   PUT /devices/{id}/deploy
   { location: "Factory A - Floor 3", status: "deployed" }

3. Device starts sending monitoring data
   POST /monitoring/data
   { device_id: 123, metrics: {...} }

4. Monitoring stores data and broadcasts via Socket.IO
```

### Device Recall Flow
```
1. Admin recalls device from field
   PUT /devices/{id}/recall
   { status: "in_stock", location: "Warehouse B" }

2. Device stops sending monitoring data
```

---

## Implementation Steps

### Step 1: Understand Current Code
- Review backend-api-v1 structure
- Follow same architecture pattern

### Step 2: Create Device Store Microservice
- Models: Device, DeviceLog
- Controllers: Device CRUD, Deploy/Recall actions
- Services: Device management logic

### Step 3: Create Monitoring Microservice
- MongoDB integration
- RabbitMQ consumer for device data
- Socket.IO for real-time updates

### Step 4: Integrate
- Device Store publishes events to RabbitMQ
- Monitoring consumes events
- Frontend connects via Socket.IO

---

## Directory Structure

```
Project/
├── backend-api-v1/           # Signing (DONE)
├── device-management/        # Device Store (TO DO)
│   ├── main.py
│   ├── controllers/
│   │   └── device_controller.py
│   ├── dal/
│   │   └── device_dao.py
│   ├── dto/
│   │   └── device_dto.py
│   ├── entities/
│   │   └── device.py
│   ├── services/
│   │   └── device_service.py
│   ├── docker/
│   └── k8s/
├── monitoring/               # Monitoring (TO DO)
│   ├── main.py
│   ├── controllers/
│   ├── dal/
│   ├── services/
│   ├── docker/
│   └── k8s/
├── docker-compose.yml
└── README.md
```

---

## Key Difference from Original Plan

| Aspect | Original Plan | This Plan |
|--------|---------------|-----------|
| Store Type | Customer-facing e-commerce | Internal inventory management |
| Orders | Customer orders with payment | No orders - just device lifecycle |
| Delivery | Shipping to customers | Deploying to field locations |
| Customers | External customers | Internal IT/Operations team |
| Primary Goal | Sell devices | Monitor deployed devices |

This is now exactly what Samsung would use internally - to monitor millions of devices AND know their inventory of spare parts.
