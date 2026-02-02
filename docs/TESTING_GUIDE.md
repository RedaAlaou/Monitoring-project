# Testing the Monitoring Microservice

## Prerequisites

Make sure you have Docker and Docker Compose installed on your system.

## Step 1: Install Dependencies

First, install the Python dependencies for the monitoring service:

```bash
cd monitoring
pip install -r requirements.txt
```

Required dependencies:
- fastapi==0.123.7
- uvicorn==0.38.0
- python-socketio==5.12.0
- python-socketio[asyncio]==5.12.0
- pymongo==4.10.1
- pika==1.3.2
- httpx==0.28.1
- pydantic==2.12.5

## Step 2: Start MongoDB (Required)

You can start MongoDB using Docker:

```bash
# Start MongoDB container
docker run -d \
  --name monitoring-mongodb \
  -p 27018:27017 \
  -v mongodb_data:/data/db \
  mongo:7
```

Or using the provided docker-compose file:

```bash
docker-compose -f docker-compose.monitoring.yml up -d mongodb
```

## Step 3: Start RabbitMQ (Optional - for event consumption)

```bash
docker run -d \
  --name monitoring-rabbitmq \
  -p 5673:5672 \
  -p 15673:15672 \
  -v rabbitmq_data:/var/lib/rabbitmq \
  rabbitmq:3-management
```

Or:

```bash
docker-compose -f docker-compose.monitoring.yml up -d rabbitmq
```

## Step 4: Run the Monitoring Service

Start the monitoring service:

```bash
cd monitoring
python main.py
```

The service will start on `http://localhost:8002`

## Step 5: Test the Endpoints

### Health Check
```bash
curl http://localhost:8002/health
```

Expected response:
```json
{"status": "healthy", "service": "monitoring"}
```

### Get Telemetry
```bash
curl http://localhost:8002/api/v1/telemetry
```

Expected response:
```json
[]
```

### Get Events
```bash
curl http://localhost:8002/api/v1/events
```

Expected response:
```json
[]
```

### Get Stats
```bash
curl http://localhost:8002/api/v1/telemetry/stats
```

Expected response:
```json
{"telemetry_count": 0, "total_devices": 0, "devices": []}
```

## Step 6: Test with Real Data

### Insert Telemetry Data via MongoDB Shell

```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017

# Switch to monitoring database
use monitoring

# Insert telemetry data
db.telemetry.insertOne({
    device_id: 1,
    device_type: "sensor",
    timestamp: new Date().toISOString(),
    data: {
        temperature: 25.5,
        humidity: 60
    }
})

# Insert device event
db.device_events.insertOne({
    device_id: 1,
    event_type: "deployed",
    timestamp: new Date().toISOString(),
    details: {
        location: "Building A",
        deployed_by: "admin"
    }
})
```

### Verify Data via API

```bash
# Get telemetry
curl http://localhost:8002/api/v1/telemetry

# Get events
curl http://localhost:8002/api/v1/telemetry?device_id=1

# Get stats
curl http://localhost:8002/api/v1/telemetry/stats
```

## Step 7: Test Socket.IO (Real-time Updates)

Create a simple HTML test file:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Socket.IO Test</title>
    <script src="https://cdn.socket.io/4.7.4/socket.io.min.js"></script>
</head>
<body>
    <h1>Monitoring Service - Real-time Test</h1>
    <div id="messages"></div>
    
    <script>
        const socket = io('http://localhost:8002');
        
        socket.on('connect', () => {
            console.log('Connected to Socket.IO');
            document.getElementById('messages').innerHTML += '<p>Connected!</p>';
        });
        
        socket.on('telemetry', (data) => {
            console.log('Telemetry:', data);
            document.getElementById('messages').innerHTML += 
                '<p>Telemetry: ' + JSON.stringify(data) + '</p>';
        });
        
        socket.on('device_event', (data) => {
            console.log('Device Event:', data);
            document.getElementById('messages').innerHTML += 
                '<p>Device Event: ' + JSON.stringify(data) + '</p>';
        });
        
        socket.on('disconnect', () => {
            console.log('Disconnected');
            document.getElementById('messages').innerHTML += '<p>Disconnected!</p>';
        });
    </script>
</body>
</html>
```

Open this file in a browser and check the console for real-time updates.

## Step 8: Run with Docker Compose

Start all monitoring infrastructure:

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

This will start:
- MongoDB (port 27018)
- RabbitMQ (ports 5673, 15673)
- Redis (port 6380)
- Monitoring service (port 8002)

Then run the service:

```bash
cd monitoring
python main.py
```

## Step 9: API Documentation

Access the FastAPI auto-generated documentation:

- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## Testing Checklist

| Test | Status |
|------|--------|
| Health endpoint | ⬜ |
| Get telemetry (empty) | ⬜ |
| Get events (empty) | ⬜ |
| Get stats (empty) | ⬜ |
| Insert data via MongoDB | ⬜ |
| Get telemetry (with data) | ⬜ |
| Get events (with data) | ⬜ |
| Get stats (with data) | ⬜ |
| Socket.IO connection | ⬜ |
| Socket.IO telemetry event | ⬜ |
| Socket.IO device_event event | ⬜ |

## Troubleshooting

### Port Already in Use
If you get an error about port 8002 being in use:
```bash
# Find and kill the process
lsof -ti:8002 | xargs kill -9

# Or use a different port in main.py
```

### MongoDB Connection Error
Make sure MongoDB is running:
```bash
docker ps | grep mongodb
```

### RabbitMQ Connection Error
Make sure RabbitMQ is running:
```bash
docker ps | grep rabbitmq
```

### Import Errors
If you get import errors, make sure you're running from the monitoring directory:
```bash
cd monitoring
python main.py
```

Or set the PYTHONPATH:
```bash
PYTHONPATH=. python main.py
```
