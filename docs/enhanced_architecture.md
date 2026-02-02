# Enhanced Architecture: Device Store + IoT Monitoring System

## Project Overview

This is a **Cloud-Native Device Store Management System with IoT Monitoring** that combines:

1. **Store Management** - Inventory, orders, delivery tracking
2. **IoT Monitoring** - Real-time data collection from deployed devices

---

## System Architecture Diagram

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
│  (PostgreSQL+     │    │  (PostgreSQL+     │    │   (MongoDB+       │
│   Redis)          │    │   Redis)          │    │   Redis+Socket.IO)│
│                   │    │                   │    │                   │
│ - User Auth       │    │ - Inventory Mgmt  │    │ - Data Ingestion  │
│ - Admin Roles     │    │ - Order Mgmt      │    │ - Real-time Data  │
│ - JWT Tokens      │    │ - Delivery Track  │    │ - Alerts          │
│                   │    │ - Device Config   │    │ - Visualisation   │
└───────────────────┘    └───────────────────┘    └───────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
            ┌─────────────┐                 ┌─────────────┐
            │   RabbitMQ  │                 │   Frontend  │
            │  (Messages) │                 │  (Socket.IO │
            └─────────────┘                 └─────────────┘
```

---

## Enhanced Device Store Microservice

### Features

#### 1. Inventory Management
- Add/edit/delete devices in stock
- Track device status:
  - `in_stock` - Available for sale
  - `reserved` - Reserved for pending order
  - `sold` - Sold but not delivered
  - `deployed` - Delivered and active
  - `maintenance` - Under maintenance
  - `defective` - Not working

#### 2. Order Management
- Create orders for devices
- Track order status:
  - `pending` - Order created
  - `confirmed` - Payment confirmed
  - `processing` - Preparing for shipment
  - `shipped` - On the way
  - `delivered` - Received by customer
  - `cancelled` - Order cancelled

#### 3. Delivery Tracking
- Track delivery status
- Confirm delivery
- Handle delivery issues

#### 4. Device Configuration
- Configure devices before deployment
- Set device parameters
- Generate device keys/tokens

### Database Schema (PostgreSQL)

**t_devices:**
```sql
CREATE TABLE t_devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'in_stock',
    specifications JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**t_orders:**
```sql
CREATE TABLE t_orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES t_users(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(10, 2),
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**t_order_items:**
```sql
CREATE TABLE t_order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES t_orders(id),
    device_id INTEGER REFERENCES t_devices(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2),
    subtotal DECIMAL(10, 2)
);
```

**t_deliveries:**
```sql
CREATE TABLE t_deliveries (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES t_orders(id),
    device_id INTEGER REFERENCES t_devices(id),
    tracking_number VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    delivery_notes TEXT
);
```

### API Endpoints

**Inventory:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/devices/` | List all devices |
| POST | `/devices/` | Add new device |
| GET | `/devices/{id}` | Get device details |
| PUT | `/devices/{id}` | Update device |
| DELETE | `/devices/{id}` | Delete device |
| PUT | `/devices/{id}/status` | Update device status |

**Orders:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders/` | List all orders |
| POST | `/orders/` | Create new order |
| GET | `/orders/{id}` | Get order details |
| PUT | `/orders/{id}/status` | Update order status |

**Deliveries:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/deliveries/` | List all deliveries |
| POST | `/deliveries/` | Create delivery |
| PUT | `/deliveries/{id}/status` | Update delivery status |
| PUT | `/deliveries/{id}/confirm` | Confirm delivery |

---

## Monitoring Microservice (Enhanced)

### Features

#### 1. Real-time Data Collection
- Listen to RabbitMQ for device data
- Store in MongoDB for time-series data
- Handle high-frequency data ingestion

#### 2. Device Health Monitoring
- Track device online/offline status
- Monitor device metrics (CPU, memory, temperature)
- Generate alerts for abnormal readings

#### 3. Historical Data Analysis
- Query historical device data
- Generate reports and statistics
- Data aggregation and filtering

#### 4. Real-time Notifications
- Socket.IO for real-time updates
- Alert notifications
- Dashboard live updates

### MongoDB Collections

**monitoring_data:**
```javascript
{
    device_id: ObjectId,
    timestamp: Date,
    metrics: {
        temperature: Number,
        humidity: Number,
        cpu_usage: Number,
        memory_usage: Number,
        battery_level: Number
    },
    location: { lat: Number, lng: Number },
    raw_data: Object
}
```

**device_alerts:**
```javascript
{
    device_id: ObjectId,
    alert_type: String,
    severity: String,
    message: String,
    acknowledged: Boolean,
    created_at: Date
}
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/monitoring/data` | Get monitoring data |
| GET | `/monitoring/data/{device_id}` | Get device data |
| GET | `/monitoring/stats` | Get statistics |
| GET | `/monitoring/alerts` | Get active alerts |
| WS | `/ws/monitoring` | Socket.IO real-time |

---

## RabbitMQ Communication Flow

```
IoT Device → Device Store → RabbitMQ → Monitoring → Frontend
```

**Exchange: `device_events`**
- `queue_data_ingestion` - Raw device data
- `queue_alerts` - Alert events
- `queue_status` - Status updates

---

## Complete Workflow Example

1. ADMIN adds device to inventory
2. CUSTOMER places order
3. ADMIN confirms order and marks device as reserved
4. ADMIN ships device
5. CUSTOMER receives and deploys device
6. Device sends real-time monitoring data
7. Monitoring Service stores and visualizes data
8. ADMIN queries monitoring data

---

## Directory Structure

```
Project/
├── backend-api-v1/           # Signing Microservice (DONE)
├── device-store/             # Device Store Microservice (TO DO)
│   ├── main.py
│   ├── controllers/
│   ├── dal/
│   ├── dto/
│   ├── entities/
│   ├── services/
│   ├── docker/
│   └── k8s/
├── monitoring/               # Monitoring Microservice (TO DO)
│   ├── main.py
│   ├── controllers/
│   ├── dal/
│   ├── dto/
│   ├── entities/
│   ├── services/
│   ├── docker/
│   └── k8s/
├── iot-simulator/            # IoT Device Simulator (TO DO)
├── nginx/
└── docker-compose.yml
```

---

## Implementation Priority

1. **Phase 1: Device Store Basics** - Inventory CRUD, status management
2. **Phase 2: Order & Delivery** - Order management, delivery tracking
3. **Phase 3: IoT Integration** - Device deployment, RabbitMQ, monitoring data
4. **Phase 4: Real-time Monitoring** - MongoDB, Socket.IO, alerts
5. **Phase 5: Advanced Features** - Analytics, ML, mobile app
