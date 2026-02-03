import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { deviceService, monitoringService } from '../services/api';
import socketService from '../services/socket';
import {
  FiArrowLeft,
  FiCpu,
  FiMapPin,
  FiActivity,
  FiThermometer,
  FiDroplet,
  FiWifi,
  FiBattery,
  FiHardDrive,
  FiMonitor,
  FiAlertTriangle,
  FiClock,
  FiRefreshCw,
  FiZap,
  FiPlay,
  FiCheck,
  FiX
} from 'react-icons/fi';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import './DeviceDetail.css';

const MAX_DATA_POINTS = 50;

const DeviceDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [device, setDevice] = useState(null);
  const [telemetryHistory, setTelemetryHistory] = useState([]);
  const [latestTelemetry, setLatestTelemetry] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  
  // Redeploy modal state
  const [showRedeployModal, setShowRedeployModal] = useState(false);
  const [redeployLocation, setRedeployLocation] = useState('');
  const [redeployNotes, setRedeployNotes] = useState('');
  const [redeployLoading, setRedeployLoading] = useState(false);
  const [redeployError, setRedeployError] = useState('');
  const [redeploySuccess, setRedeploySuccess] = useState('');

  // Fetch device details
  const fetchDevice = useCallback(async () => {
    try {
      const response = await deviceService.getDeviceById(id);
      setDevice(response);
    } catch (err) {
      console.error('Error fetching device:', err);
      setError('Failed to load device details');
    }
  }, [id]);

  // Fetch telemetry history
  const fetchTelemetryHistory = useCallback(async () => {
    try {
      const response = await monitoringService.getTelemetry(id, 50);
      const formattedData = response.map(t => ({
        ...t,
        time: new Date(t.timestamp).toLocaleTimeString()
      })).reverse();
      setTelemetryHistory(formattedData);
      if (formattedData.length > 0) {
        setLatestTelemetry(formattedData[formattedData.length - 1]);
      }
    } catch (err) {
      console.error('Error fetching telemetry:', err);
    }
  }, [id]);

  // Fetch device events
  const fetchEvents = useCallback(async () => {
    try {
      const response = await monitoringService.getEvents(id, 20);
      setEvents(response);
    } catch (err) {
      console.error('Error fetching events:', err);
    }
  }, [id]);

  // Initial data load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchDevice(), fetchTelemetryHistory(), fetchEvents()]);
      setLoading(false);
    };
    loadData();
  }, [fetchDevice, fetchTelemetryHistory, fetchEvents]);

  // Socket.IO real-time updates
  useEffect(() => {
    const socket = socketService.connect();
    
    socket.on('connect', () => {
      setIsConnected(true);
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
    });

    // Handle telemetry updates
    const handleTelemetry = (data) => {
      // Only update if it's for this device
      if (data.device_id === parseInt(id)) {
        const formattedData = {
          ...data,
          time: new Date(data.timestamp).toLocaleTimeString()
        };
        
        setLatestTelemetry(formattedData);
        setTelemetryHistory(prev => {
          const newHistory = [...prev, formattedData];
          return newHistory.slice(-MAX_DATA_POINTS);
        });
      }
    };

    // Handle device events
    const handleEvent = (data) => {
      if (data.device_id === parseInt(id)) {
        setEvents(prev => [data, ...prev].slice(0, 20));
      }
    };

    socketService.onTelemetry(handleTelemetry);
    socketService.onDeviceEvent(handleEvent);

    return () => {
      socketService.off('telemetry', handleTelemetry);
      socketService.off('device_event', handleEvent);
    };
  }, [id]);

  const getStatusColor = (status) => {
    const colors = {
      deployed: '#10b981',
      in_stock: '#3b82f6',
      maintenance: '#f59e0b',
      reserved: '#8b5cf6'
    };
    return colors[status] || '#6b7280';
  };

  const getEventSeverityClass = (severity) => {
    return severity === 'high' ? 'severity-high' : 'severity-normal';
  };

  // Handle redeploy from maintenance
  const handleRedeploy = async (e) => {
    e.preventDefault();
    setRedeployError('');
    setRedeploySuccess('');
    setRedeployLoading(true);

    try {
      await deviceService.redeployFromMaintenance(id, {
        location: redeployLocation || device.location,
        notes: redeployNotes || 'Redeployed from maintenance'
      });
      setRedeploySuccess('Device successfully redeployed!');
      // Refresh device data
      await fetchDevice();
      // Close modal after a short delay
      setTimeout(() => {
        setShowRedeployModal(false);
        setRedeployLocation('');
        setRedeployNotes('');
        setRedeploySuccess('');
      }, 1500);
    } catch (err) {
      console.error('Error redeploying device:', err);
      setRedeployError(err.response?.data?.detail || 'Failed to redeploy device. Please try again.');
    } finally {
      setRedeployLoading(false);
    }
  };

  // Close modal handler
  const closeRedeployModal = () => {
    setShowRedeployModal(false);
    setRedeployLocation('');
    setRedeployNotes('');
    setRedeployError('');
    setRedeploySuccess('');
  };

  if (loading) {
    return (
      <div className="device-detail">
        <div className="loader">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error || !device) {
    return (
      <div className="device-detail">
        <div className="error-state">
          <FiAlertTriangle size={48} />
          <h2>{error || 'Device not found'}</h2>
          <button className="btn btn-primary" onClick={() => navigate(-1)}>
            <FiArrowLeft /> Go Back
          </button>
        </div>
      </div>
    );
  }

  // Determine what metrics to show based on device type
  const isComputer = device.type === 'computer';
  const isSensor = ['sensor', 'iot_sensor'].includes(device.type);

  return (
    <div className="device-detail">
      {/* Header */}
      <div className="detail-header">
        <button className="btn btn-ghost" onClick={() => navigate(-1)}>
          <FiArrowLeft /> Back
        </button>
        <div className="header-info">
          <h1>{device.name}</h1>
          <div className="header-meta">
            <span className="serial-number">
              <code>{device.serial_number}</code>
            </span>
            <span 
              className="status-badge"
              style={{ backgroundColor: getStatusColor(device.status) }}
            >
              {device.status?.replace('_', ' ')}
            </span>
            <span className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
              <FiWifi />
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>
        <div className="header-actions">
          {device.status === 'maintenance' && (
            <button 
              className="btn btn-success" 
              onClick={() => setShowRedeployModal(true)}
            >
              <FiPlay /> Redeploy
            </button>
          )}
          <button className="btn btn-secondary" onClick={() => {
            fetchDevice();
            fetchTelemetryHistory();
            fetchEvents();
          }}>
            <FiRefreshCw /> Refresh
          </button>
        </div>
      </div>

      {/* Device Info Cards */}
      <div className="info-grid">
        <div className="info-card">
          <FiCpu className="info-icon" />
          <div className="info-content">
            <span className="info-label">Type</span>
            <span className="info-value">{device.type?.replace('_', ' ')}</span>
          </div>
        </div>
        <div className="info-card">
          <FiMapPin className="info-icon" />
          <div className="info-content">
            <span className="info-label">Location</span>
            <span className="info-value">{device.location || 'Not set'}</span>
          </div>
        </div>
        <div className="info-card">
          <FiClock className="info-icon" />
          <div className="info-content">
            <span className="info-label">Last Update</span>
            <span className="info-value">
              {latestTelemetry?.time || 'No data'}
            </span>
          </div>
        </div>
        <div className="info-card">
          <FiActivity className="info-icon" />
          <div className="info-content">
            <span className="info-label">Data Points</span>
            <span className="info-value">{telemetryHistory.length}</span>
          </div>
        </div>
      </div>

      {/* Real-time Metrics */}
      {latestTelemetry && (
        <div className="metrics-section">
          <h2><FiZap /> Real-Time Metrics</h2>
          <div className="metrics-grid">
            {/* Computer-specific metrics */}
            {(latestTelemetry.cpu_usage !== undefined) && (
              <div className="metric-card">
                <div className="metric-header">
                  <FiMonitor className="metric-icon cpu" />
                  <span>CPU Usage</span>
                </div>
                <div className="metric-value">
                  {latestTelemetry.cpu_usage?.toFixed(1)}%
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill cpu" 
                    style={{ width: `${Math.min(latestTelemetry.cpu_usage, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {(latestTelemetry.ram_percent !== undefined) && (
              <div className="metric-card">
                <div className="metric-header">
                  <FiHardDrive className="metric-icon ram" />
                  <span>RAM Usage</span>
                </div>
                <div className="metric-value">
                  {latestTelemetry.ram_percent?.toFixed(1)}%
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill ram" 
                    style={{ width: `${Math.min(latestTelemetry.ram_percent, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {(latestTelemetry.gpu_usage !== undefined) && (
              <div className="metric-card">
                <div className="metric-header">
                  <FiCpu className="metric-icon gpu" />
                  <span>GPU Usage</span>
                </div>
                <div className="metric-value">
                  {latestTelemetry.gpu_usage?.toFixed(1)}%
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill gpu" 
                    style={{ width: `${Math.min(latestTelemetry.gpu_usage, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {(latestTelemetry.disk_usage_percent !== undefined) && (
              <div className="metric-card">
                <div className="metric-header">
                  <FiHardDrive className="metric-icon disk" />
                  <span>Disk Usage</span>
                </div>
                <div className="metric-value">
                  {latestTelemetry.disk_usage_percent?.toFixed(1)}%
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill disk" 
                    style={{ width: `${Math.min(latestTelemetry.disk_usage_percent, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {/* Sensor-specific metrics */}
            {(latestTelemetry.temperature !== undefined) && (
              <div className="metric-card">
                <div className="metric-header">
                  <FiThermometer className="metric-icon temp" />
                  <span>Temperature</span>
                </div>
                <div className="metric-value">
                  {latestTelemetry.temperature?.toFixed(1)}°C
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill temp" 
                    style={{ width: `${Math.min((latestTelemetry.temperature / 50) * 100, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {(latestTelemetry.humidity !== undefined) && (
              <div className="metric-card">
                <div className="metric-header">
                  <FiDroplet className="metric-icon humidity" />
                  <span>Humidity</span>
                </div>
                <div className="metric-value">
                  {latestTelemetry.humidity?.toFixed(1)}%
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill humidity" 
                    style={{ width: `${Math.min(latestTelemetry.humidity, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {(latestTelemetry.battery_level !== undefined) && (
              <div className="metric-card">
                <div className="metric-header">
                  <FiBattery className="metric-icon battery" />
                  <span>Battery</span>
                </div>
                <div className="metric-value">
                  {latestTelemetry.battery_level?.toFixed(1)}%
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill battery" 
                    style={{ width: `${Math.min(latestTelemetry.battery_level, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {(latestTelemetry.value !== undefined && !latestTelemetry.temperature) && (
              <div className="metric-card">
                <div className="metric-header">
                  <FiActivity className="metric-icon value" />
                  <span>Value</span>
                </div>
                <div className="metric-value">
                  {latestTelemetry.value?.toFixed(2)}
                </div>
                <div className="metric-bar">
                  <div 
                    className="metric-fill value" 
                    style={{ width: `${Math.min(latestTelemetry.value, 100)}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Charts Section */}
      <div className="charts-section">
        <h2><FiActivity /> Telemetry History</h2>
        <div className="charts-grid">
          {/* CPU/Temperature Chart */}
          {telemetryHistory.length > 0 && (telemetryHistory[0].cpu_usage !== undefined || telemetryHistory[0].temperature !== undefined) && (
            <div className="chart-card">
              <h3>{telemetryHistory[0].cpu_usage !== undefined ? 'CPU Usage' : 'Temperature'}</h3>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={telemetryHistory}>
                  <defs>
                    <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="time" stroke="#666" fontSize={10} />
                  <YAxis stroke="#666" domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ background: '#1a1a2e', border: '1px solid #333' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey={telemetryHistory[0].cpu_usage !== undefined ? "cpu_usage" : "temperature"}
                    stroke="#3b82f6" 
                    fill="url(#colorCpu)" 
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* RAM/Humidity Chart */}
          {telemetryHistory.length > 0 && (telemetryHistory[0].ram_percent !== undefined || telemetryHistory[0].humidity !== undefined) && (
            <div className="chart-card">
              <h3>{telemetryHistory[0].ram_percent !== undefined ? 'RAM Usage' : 'Humidity'}</h3>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={telemetryHistory}>
                  <defs>
                    <linearGradient id="colorRam" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="time" stroke="#666" fontSize={10} />
                  <YAxis stroke="#666" domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ background: '#1a1a2e', border: '1px solid #333' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey={telemetryHistory[0].ram_percent !== undefined ? "ram_percent" : "humidity"}
                    stroke="#10b981" 
                    fill="url(#colorRam)" 
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* GPU/Battery Chart */}
          {telemetryHistory.length > 0 && (telemetryHistory[0].gpu_usage !== undefined || telemetryHistory[0].battery_level !== undefined) && (
            <div className="chart-card">
              <h3>{telemetryHistory[0].gpu_usage !== undefined ? 'GPU Usage' : 'Battery Level'}</h3>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={telemetryHistory}>
                  <defs>
                    <linearGradient id="colorGpu" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="time" stroke="#666" fontSize={10} />
                  <YAxis stroke="#666" domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ background: '#1a1a2e', border: '1px solid #333' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey={telemetryHistory[0].gpu_usage !== undefined ? "gpu_usage" : "battery_level"}
                    stroke="#f59e0b" 
                    fill="url(#colorGpu)" 
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Disk/Pressure Chart */}
          {telemetryHistory.length > 0 && (telemetryHistory[0].disk_usage_percent !== undefined || telemetryHistory[0].pressure !== undefined) && (
            <div className="chart-card">
              <h3>{telemetryHistory[0].disk_usage_percent !== undefined ? 'Disk Usage' : 'Pressure'}</h3>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={telemetryHistory}>
                  <defs>
                    <linearGradient id="colorDisk" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="time" stroke="#666" fontSize={10} />
                  <YAxis stroke="#666" />
                  <Tooltip 
                    contentStyle={{ background: '#1a1a2e', border: '1px solid #333' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey={telemetryHistory[0].disk_usage_percent !== undefined ? "disk_usage_percent" : "pressure"}
                    stroke="#8b5cf6" 
                    fill="url(#colorDisk)" 
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Events Section */}
      <div className="events-section">
        <h2><FiAlertTriangle /> Recent Events</h2>
        {events.length === 0 ? (
          <div className="no-events">
            <FiActivity />
            <p>No events recorded</p>
          </div>
        ) : (
          <div className="events-list">
            {events.map((event, index) => (
              <div 
                key={event._id || index} 
                className={`event-item ${getEventSeverityClass(event.details?.severity)}`}
              >
                <div className="event-icon">
                  <FiAlertTriangle />
                </div>
                <div className="event-content">
                  <div className="event-header">
                    <span className="event-type">{event.event_type}</span>
                    <span className="event-time">
                      {new Date(event.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="event-message">{event.message}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Device Details */}
      <div className="details-section">
        <h2><FiCpu /> Device Details</h2>
        <div className="details-grid">
          <div className="detail-item">
            <span className="detail-label">ID</span>
            <span className="detail-value">{device.id}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Serial Number</span>
            <span className="detail-value"><code>{device.serial_number}</code></span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Type</span>
            <span className="detail-value">{device.type}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Status</span>
            <span className="detail-value">{device.status}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Location</span>
            <span className="detail-value">{device.location || 'Not set'}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Description</span>
            <span className="detail-value">{device.description || 'No description'}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Created</span>
            <span className="detail-value">
              {device.created_at ? new Date(device.created_at).toLocaleString() : '-'}
            </span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Updated</span>
            <span className="detail-value">
              {device.updated_at ? new Date(device.updated_at).toLocaleString() : '-'}
            </span>
          </div>
        </div>
        {device.specifications && (
          <div className="specifications">
            <h3>Specifications</h3>
            <pre>{JSON.stringify(
              typeof device.specifications === 'string' 
                ? (() => { try { return JSON.parse(device.specifications); } catch { return device.specifications; } })()
                : device.specifications, 
              null, 2
            )}</pre>
          </div>
        )}
      </div>

      {/* Redeploy Modal */}
      {showRedeployModal && (
        <div className="modal-overlay" onClick={closeRedeployModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><FiPlay /> Redeploy Device</h2>
              <button className="btn btn-ghost modal-close" onClick={closeRedeployModal}>
                <FiX />
              </button>
            </div>
            
            <form onSubmit={handleRedeploy}>
              <div className="modal-body">
                <p className="modal-description">
                  Redeploy <strong>{device.name}</strong> from maintenance status back to active deployment.
                </p>
                
                {redeployError && (
                  <div className="alert alert-error">
                    <FiAlertTriangle /> {redeployError}
                  </div>
                )}
                
                {redeploySuccess && (
                  <div className="alert alert-success">
                    <FiCheck /> {redeploySuccess}
                  </div>
                )}
                
                <div className="form-group">
                  <label htmlFor="redeployLocation">Deployment Location</label>
                  <input
                    type="text"
                    id="redeployLocation"
                    className="form-input"
                    value={redeployLocation}
                    onChange={(e) => setRedeployLocation(e.target.value)}
                    placeholder={device.location || 'Enter deployment location'}
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="redeployNotes">Notes (Optional)</label>
                  <textarea
                    id="redeployNotes"
                    className="form-input form-textarea"
                    value={redeployNotes}
                    onChange={(e) => setRedeployNotes(e.target.value)}
                    placeholder="Add any notes about this redeployment..."
                    rows={3}
                  />
                </div>
              </div>
              
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={closeRedeployModal}
                  disabled={redeployLoading}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-success"
                  disabled={redeployLoading || redeploySuccess}
                >
                  {redeployLoading ? (
                    <>
                      <span className="spinner-small"></span> Redeploying...
                    </>
                  ) : (
                    <>
                      <FiPlay /> Redeploy Device
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DeviceDetail;
