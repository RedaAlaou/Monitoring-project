import { io } from 'socket.io-client';

const MONITORING_URL = process.env.REACT_APP_MONITORING_URL || 'http://localhost:8002';

class SocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
  }

  connect() {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.socket = io(MONITORING_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    this.socket.on('connect', () => {
      console.log('🔌 Socket.IO connected:', this.socket.id);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('🔌 Socket.IO disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('🔌 Socket.IO connection error:', error);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // Subscribe to telemetry updates
  onTelemetry(callback) {
    if (!this.socket) this.connect();
    
    this.socket.on('telemetry', (data) => {
      console.log('📡 Telemetry received:', data);
      callback(data);
    });
  }

  // Subscribe to device events
  onDeviceEvent(callback) {
    if (!this.socket) this.connect();
    
    this.socket.on('device_event', (data) => {
      console.log('⚡ Device event received:', data);
      callback(data);
    });
  }

  // Subscribe to any event
  on(event, callback) {
    if (!this.socket) this.connect();
    this.socket.on(event, callback);
  }

  // Unsubscribe from event
  off(event, callback) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  // Get socket instance
  getSocket() {
    return this.socket;
  }
}

// Singleton instance
const socketService = new SocketService();
export default socketService;
