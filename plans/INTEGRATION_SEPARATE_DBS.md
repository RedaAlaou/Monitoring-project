# Microservices Integration with Separate Databases

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Network                        │
│                    net-monitoring-app                        │
└─────────────────────────────────────────────────────────────┘
                              │
     ┌────────────────────────┼────────────────────────┐
     ▼                        ▼                        ▼
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│   Signing   │        │  Device     │        │  Database   │
│   Service   │◄──────►│  Management │◄──────►│  (PostgreSQL)
│  (backend)  │  JWT   │  Service    │        │             │
│             │        │             │        │  - db_auth  │
│  Port:8000  │        │  Port:8001  │        │  - db_device│
└─────────────┘        └─────────────┘        └─────────────┘
```

## Docker Compose for Both Services

**Create:** `docker-compose.integration.yml` at project root

```yaml
version: '3.8'

services:
  # Signing Service (backend-api-v1)
  signing:
    build: ./backend-api-v1
    container_name: signing-ms
    environment:
      - SERVER_DB=db
      - NAME_DB=db_auth
      - USER_DB=admin
      - PASSWORD_DB=1234
    ports:
      - "8000:8000"
    volumes:
      - ./backend-api-v1/logs:/app/logs
    networks:
      - net-monitoring-app
    depends_on:
      - db

  # Device Management Service
  device-management:
    build: ./device-management
    container_name: device-management-ms
    environment:
      - SERVER_DB=db
      - NAME_DB=db_device_management
      - USER_DB=admin
      - PASSWORD_DB=1234
    ports:
      - "8001:8001"
    volumes:
      - ./device-management/logs:/app/logs
    networks:
      - net-monitoring-app
    depends_on:
      - db

  # Shared PostgreSQL with multiple databases
  db:
    image: postgres:alpine
    container_name: postgresql-shared
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=1234
      - POSTGRES_MULTIPLE_DATABASES=db_auth,db_device_management
    ports:
      - "5432:5432"
    networks:
      - net-monitoring-app
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./db/init-multiple-dbs.sh:/docker-entrypoint-initdb.d/init-multiple-dbs.sh

networks:
  net-monitoring-app:
    driver: bridge

volumes:
  pgdata:
```

## Database Initialization Script

**Create:** `db/init-multiple-dbs.sh`

```bash
#!/bin/bash
set -e
set -u

function create_user_and_database() {
    local database=$1
    echo "Creating user and database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE USER $database WITH PASSWORD '$POSTGRES_PASSWORD';
        CREATE DATABASE $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        create_user_and_database $db
    done
fi
```

## Step-by-Step Instructions

### Step 1: Create the db folder and init script

```bash
mkdir -p db
```

The init script will be created by me.

### Step 2: Run both services

```bash
# Stop any existing containers
docker-compose -f backend-api-v1/docker-compose.yml down
docker-compose -f device-management/docker/docker-compose.yml down

# Start all services together
docker-compose -f docker-compose.integration.yml up -d
```

### Step 3: Check services are running

```bash
docker ps
```

You should see:
- `signing-ms` on port 8000
- `device-management-ms` on port 8001
- `postgresql-shared` on port 5432

### Step 4: Test Signing Service

**Register a user:**
```bash
curl -X POST "http://localhost:8000/users/add" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.com","password":"admin123"}'
```

**Login to get JWT token:**
```bash
curl -X POST "http://localhost:8000/users/auth" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.com","password":"admin123"}'
```

**Save the token from the response:**
```json
{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...","payload":{"sub":"admin@company.com","role":false}}
```

### Step 5: Test Device Management (with JWT)

**Create a device (with token):**
```bash
TOKEN="your_token_here"

curl -X POST "http://localhost:8001/api/v1/devices/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Temperature Sensor 1","type":"sensor","serial_number":"SN-001","location":"Warehouse A"}'
```

**List devices (with token):**
```bash
curl "http://localhost:8001/api/v1/devices/" \
  -H "Authorization: Bearer $TOKEN"
```

### Step 6: Test without token (should fail)

```bash
# Should return 401 Unauthorized
curl "http://localhost:8001/api/v1/devices/"
```

## Files to Create

| File | Purpose |
|------|---------|
| `docker-compose.integration.yml` | Run both services + DB |
| `db/init-multiple-dbs.sh` | Initialize multiple databases |
| `device-management/helpers/jwt_utils.py` | JWT utilities |
| Updated `device-management/controllers/device_controller.py` | Add auth |
| Updated `device-management/requirements.txt` | Add python-jose |

## Service Endpoints

### Signing Service (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/add` | Register user |
| POST | `/users/auth` | Login → get JWT |
| POST | `/users/verify-token` | Verify token |
| GET | `/users/` | List users (requires auth) |

### Device Management Service (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/devices/` | Create device (requires auth) |
| GET | `/api/v1/devices/` | List devices (requires auth) |
| PUT | `/api/v1/devices/{id}/deploy` | Deploy device (requires auth) |
| PUT | `/api/v1/devices/{id}/recall` | Recall device (requires auth) |
| GET | `/health` | Health check |

## Stopping Services

```bash
docker-compose -f docker-compose.integration.yml down
```
