# React Frontend for Microservices Testing

## Overview
A React application to test and interact with:
- **Signing Service** (authentication)
- **Device Management Service** (device CRUD + lifecycle)

## Tech Stack
- React 18 with TypeScript
- Vite (fast build tool)
- Tailwind CSS (styling)
- Axios (HTTP client)
- React Router (navigation)
- JWT decode for token handling

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── Navbar.tsx
│   │   ├── PrivateRoute.tsx
│   │   └── Loading.tsx
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── DeviceList.tsx
│   │   ├── DeviceForm.tsx
│   │   └── DeviceDetails.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── authService.ts
│   │   └── deviceService.ts
│   ├── context/
│   │   └── AuthContext.tsx
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Features

### 1. Login Page
- Email/password form
- JWT token storage in localStorage
- Error handling

### 2. Dashboard
- Overview statistics
- Total devices
- Devices by status (in_stock, deployed, maintenance)
- Quick actions

### 3. Device List
- Table view of all devices
- Filter by status
- Search by name/serial
- Pagination

### 4. Device Management
- Create new device
- Edit device details
- Deploy device to field
- Recall device to stock
- Send to maintenance
- View device history

## API Integration

### Signing Service (Port 8000)
```typescript
// POST /users/auth
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  token: string;
  payload: {
    sub: string;  // email
    role: boolean; // is_admin
  };
}
```

### Device Management Service (Port 8001)
```typescript
// GET /api/v1/devices/
interface Device {
  id: number;
  name: string;
  type: string;
  serial_number: string;
  description: string;
  status: 'in_stock' | 'reserved' | 'deployed' | 'maintenance' | 'retired';
  location: string;
  specifications: string;
  created_at: string;
  updated_at: string;
}

// POST /api/v1/devices/
interface DeviceRequest {
  name: string;
  type: 'sensor' | 'gateway' | 'actuator' | 'controller' | 'other';
  serial_number: string;
  description?: string;
  location?: string;
  specifications?: string;
}

// PUT /api/v1/devices/{id}/deploy
interface DeployRequest {
  location: string;
  notes?: string;
}
```

## Step-by-Step Implementation Plan

### Step 1: Initialize React Project
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install axios react-router-dom jwt-decode tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 2: Configure Tailwind CSS
Update `tailwind.config.js`:
```javascript
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
```

Add to `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 3: Create API Service
Create `src/services/api.ts`:
```typescript
import axios from 'axios';

const API_SIGNING = 'http://localhost:8000/users';
const API_DEVICE = 'http://localhost:8001/api/v1/devices';

const api = axios.create({
  headers: { 'Content-Type': 'application/json' },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export { API_SIGNING, API_DEVICE };
export default api;
```

### Step 4: Create Auth Context
Manage login state across the app.

### Step 5: Create Pages
- Login.tsx - Authentication form
- DeviceList.tsx - Device table with filters
- DeviceForm.tsx - Create/edit device

## Docker Setup for Frontend

**Create:** `frontend/Dockerfile`
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

**Update docker-compose.yml:**
```yaml
services:
  frontend:
    build: ./frontend
    container_name: frontend-dev
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - CHOKIDAR_USEPOLLING=true
```

## Running the Application

### Development Mode
```bash
cd frontend
npm run dev
```

Access at: `http://localhost:5173`

### Docker Mode
```bash
docker-compose up -d frontend
```

## User Flow

1. **Login Screen**
   - Enter email/password
   - Click "Login"
   - On success → redirect to Dashboard

2. **Dashboard**
   - See device statistics
   - Click "View Devices" to see full list

3. **Device List**
   - See all devices in table
   - Filter by status dropdown
   - Search by name/serial
   - Click "Add Device" to create new

4. **Add Device Modal**
   - Fill form with device details
   - Click "Save"

5. **Device Actions**
   - Deploy: Click "Deploy" → enter location
   - Recall: Click "Recall" → confirm
   - Maintenance: Click "Maintenance" → send for repair

## Next Steps

1. ✅ Create project plan
2. ⬜ Initialize React project
3. ⬜ Set up Tailwind CSS
4. ⬜ Create API services
5. ⬜ Build Auth context
6. ⬜ Create all pages and components
7. ⬜ Add Docker support
8. ⬜ Test with both backend services

Shall I start implementing the React frontend?