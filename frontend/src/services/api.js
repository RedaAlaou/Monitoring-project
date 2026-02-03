import axios from 'axios';

// API Base URLs
const AUTH_API_URL = process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8000';
const DEVICE_API_URL = process.env.REACT_APP_DEVICE_API_URL || 'http://localhost:8001';
const MONITORING_API_URL = process.env.REACT_APP_MONITORING_API_URL || 'http://localhost:8002';

// Create axios instances
const authApi = axios.create({
  baseURL: AUTH_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const deviceApi = axios.create({
  baseURL: DEVICE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const monitoringApi = axios.create({
  baseURL: MONITORING_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
deviceApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 responses
deviceApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authService = {
  login: async (email, password) => {
    const response = await authApi.post('/users/auth', { email, password });
    return response.data;
  },
  
  register: async (email, password) => {
    const response = await authApi.post('/users/add', { email, password });
    return response.data;
  },
};

// Device API calls
export const deviceService = {
  // Get all devices with optional filters
  getAllDevices: async (params = {}) => {
    const response = await deviceApi.get('/api/v1/devices/', { params });
    return response.data;
  },
  
  // Get devices by status
  getInStockDevices: async () => {
    const response = await deviceApi.get('/api/v1/devices/in_stock');
    return response.data;
  },
  
  getDeployedDevices: async () => {
    const response = await deviceApi.get('/api/v1/devices/deployed');
    return response.data;
  },
  
  getMaintenanceDevices: async () => {
    const response = await deviceApi.get('/api/v1/devices/maintenance');
    return response.data;
  },
  
  // Get single device
  getDeviceById: async (id) => {
    const response = await deviceApi.get(`/api/v1/devices/${id}`);
    return response.data;
  },
  
  // Create device
  createDevice: async (deviceData) => {
    const response = await deviceApi.post('/api/v1/devices/', deviceData);
    return response.data;
  },
  
  // Update device
  updateDevice: async (id, deviceData) => {
    const response = await deviceApi.put(`/api/v1/devices/${id}`, deviceData);
    return response.data;
  },
  
  // Delete device
  deleteDevice: async (id) => {
    const response = await deviceApi.delete(`/api/v1/devices/${id}`);
    return response.data;
  },
  
  // Deploy device
  deployDevice: async (id, deployData) => {
    const response = await deviceApi.put(`/api/v1/devices/${id}/deploy`, deployData);
    return response.data;
  },
  
  // Recall device
  recallDevice: async (id, recallData) => {
    const response = await deviceApi.put(`/api/v1/devices/${id}/recall`, recallData);
    return response.data;
  },
  
  // Set maintenance
  setMaintenance: async (id, maintenanceData) => {
    const response = await deviceApi.put(`/api/v1/devices/${id}/maintenance`, maintenanceData);
    return response.data;
  },

  // Update device status
  updateDeviceStatus: async (id, statusData) => {
    const response = await deviceApi.put(`/api/v1/devices/${id}/status`, statusData);
    return response.data;
  },

  // Redeploy device from maintenance
  redeployFromMaintenance: async (id, redeployData) => {
    const response = await deviceApi.put(`/api/v1/devices/${id}/deploy`, redeployData);
    return response.data;
  },
};

// Monitoring API calls
export const monitoringService = {
  // Get telemetry data
  getTelemetry: async (deviceId = null, limit = 100) => {
    const params = { limit };
    if (deviceId) params.device_id = deviceId;
    const response = await monitoringApi.get('/api/v1/telemetry/', { params });
    return response.data;
  },

  // Get telemetry stats
  getTelemetryStats: async () => {
    const response = await monitoringApi.get('/api/v1/telemetry/stats');
    return response.data;
  },

  // Get device events
  getEvents: async (deviceId = null, limit = 50) => {
    const params = { limit };
    if (deviceId) params.device_id = deviceId;
    const response = await monitoringApi.get('/api/v1/events/', { params });
    return response.data;
  },
};

export { authApi, deviceApi, monitoringApi };
