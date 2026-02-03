# IoT Monitoring Frontend

A React-based dashboard for the IoT Monitoring System.

## Features

- **Authentication**: Login and Register pages with JWT-based authentication
- **Dashboard**: Overview of all devices with status statistics
- **IoT Devices**: Manage sensors, gateways, actuators, and controllers
- **End Devices**: Manage computers, servers, and edge devices

## Tech Stack

- React 18
- React Router v6
- Axios for API calls
- React Icons
- CSS Custom Properties for theming

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend services running (Auth on port 8000, Device Management on port 8001)

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will run at http://localhost:3000

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_AUTH_API_URL=http://localhost:8000
REACT_APP_DEVICE_API_URL=http://localhost:8001
```

## Pages

### Login (`/login`)
- Email and password authentication
- JWT token stored in localStorage

### Register (`/register`)
- Create new user account
- Fields: First name, Last name, Email, Password

### Dashboard (`/`)
- Device statistics (Total, Deployed, In Stock, Maintenance)
- Table listing all devices

### IoT Devices (`/iot-devices`)
- View, create, edit, and delete IoT devices
- Device types: Sensor, Gateway, Actuator, Controller
- Actions: Deploy, Maintenance, Delete

### End Devices (`/end-devices`)
- View, create, edit, and delete end devices
- Device types: Computer, Server, Edge Device, GPU Node
- Actions: Deploy, Maintenance, Delete

## Docker

Build and run with Docker:

```bash
docker build -t iot-frontend .
docker run -p 3000:3000 iot-frontend
```

Or use docker-compose from the project root:

```bash
docker-compose -f docker-compose.frontend.yml up
```

## API Integration

The frontend connects to two backend services:

1. **Auth Service** (Port 8000)
   - `POST /users/auth` - Login
   - `POST /users/` - Register

2. **Device Management Service** (Port 8001)
   - `GET /api/v1/devices/` - List all devices
   - `POST /api/v1/devices/` - Create device
   - `PUT /api/v1/devices/{id}` - Update device
   - `DELETE /api/v1/devices/{id}` - Delete device
   - `PUT /api/v1/devices/{id}/deploy` - Deploy device
   - `PUT /api/v1/devices/{id}/maintenance` - Set maintenance

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── Layout.js
│   │   ├── Layout.css
│   │   └── PrivateRoute.js
│   ├── context/
│   │   └── AuthContext.js
│   ├── pages/
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── Dashboard.js
│   │   ├── IoTDevices.js
│   │   ├── EndDevices.js
│   │   └── *.css
│   ├── services/
│   │   └── api.js
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
├── Dockerfile
├── package.json
└── README.md
```
