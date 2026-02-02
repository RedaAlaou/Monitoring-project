# JWT Authentication Integration Plan

## Overview
Integrate Device Management service with Signing service (backend-api-v1) using JWT authentication.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway (nginx)                   │
│                    (To be added later)                       │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          ▼                                       ▼
┌─────────────────────┐               ┌─────────────────────┐
│    Signing Service  │               │  Device Management  │
│   (backend-api-v1)  │               │      Service        │
│                     │               │                     │
│  - Port: 8000       │               │  - Port: 8001       │
│  - JWT Auth         │               │  - JWT Auth         │
│  - PostgreSQL       │               │  - PostgreSQL       │
└─────────────────────┘               └─────────────────────┘
```

## Current Authentication Flow

**Signing Service (backend-api-v1):**
1. `POST /users/auth` → Returns JWT token
2. All protected endpoints require Bearer token
3. Token contains: `sub` (email), `role` (is_admin)

## Integration Steps

### Step 3.1: Add JWT Utilities to Device Management

**Create:** `device-management/helpers/jwt_utils.py`

```python
from jose import jwt, JWTError
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Same SECRET_KEY as signing service
SECRET_KEY = "$argon2id$v=19$m=65536,t=3,p=4$hT18aCPZ5AFxQ2ncYkRkWg$5UvBttA1brZmn6Bmf1T0NgKaYaqUzMV1pvWNxDp5pFc"
ALGORITHM = "HS256"

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload:
            return payload
    except JWTError:
        return None
    return None

def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload."""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload
```

### Step 3.2: Add Authentication to Device Controller

**Update:** `device-management/controllers/device_controller.py`

Add authentication dependency:

```python
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from helpers.jwt_utils import verify_token

router = APIRouter(prefix="/devices", tags=["devices"])
http_bearer = HTTPBearer()

def get_current_user(token: HTTPAuthorizationCredentials = Security(http_bearer)):
    """Dependency to get current authenticated user."""
    return verify_token(token.credentials)

# Add to all protected endpoints:
# - GET / (list devices)
# - POST / (create device)
# - PUT /{id}
# - DELETE /{id}
# - PUT /{id}/deploy
# - PUT /{id}/recall
# - PUT /{id}/maintenance
```

### Step 3.3: Update Docker Compose

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
      - net-microservices
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
      - net-microservices
    depends_on:
      - db

  # Shared PostgreSQL Database
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
      - net-microservices
    volumes:
      - pgdata:/var/lib/postgresql/data

networks:
  net-microservices:
    driver: bridge

volumes:
  pgdata:
```

### Step 3.4: Create init script for multiple databases

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

**Update Dockerfile for db:**
```dockerfile
FROM postgres:alpine
COPY init-multiple-dbs.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-multiple-dbs.sh
```

## Testing Flow

### Step 1: Start services
```bash
docker-compose -f docker-compose.integration.yml up -d
```

### Step 2: Register a user (Signing Service)
```bash
curl -X POST "http://localhost:8000/users/add" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.com","password":"admin123"}'
```

### Step 3: Login to get JWT token
```bash
curl -X POST "http://localhost:8000/users/auth" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.com","password":"admin123"}'
```

### Step 4: Use token to access Device Management
```bash
# Save the token from step 3
TOKEN="your_jwt_token_here"

# Create a device (authenticated)
curl -X POST "http://localhost:8001/api/v1/devices/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Temp Sensor 1","type":"sensor","serial_number":"SN-001"}'

# List devices (authenticated)
curl "http://localhost:8001/api/v1/devices/" \
  -H "Authorization: Bearer $TOKEN"
```

### Step 5: Test without token (should fail)
```bash
# Should return 403 Forbidden
curl "http://localhost:8001/api/v1/devices/"
```

## File Changes Summary

| File | Action |
|------|--------|
| `device-management/helpers/jwt_utils.py` | Create |
| `device-management/helpers/config.py` | Update (add SECRET_KEY) |
| `device-management/controllers/device_controller.py` | Update (add auth) |
| `device-management/requirements.txt` | Update (add python-jose) |
| `docker-compose.integration.yml` | Create (at project root) |
| `db/init-multiple-dbs.sh` | Create |

## Next Steps

1. ✅ Plan the integration
2. ⬜ Create JWT utilities
3. ⬜ Update device controller with authentication
4. ⬜ Update docker-compose for both services
5. ⬜ Test the complete flow
