import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { deviceService } from '../services/api';
import { FiCpu, FiCheckCircle, FiTool, FiPackage, FiAlertCircle, FiRefreshCw, FiActivity } from 'react-icons/fi';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [devices, setDevices] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    deployed: 0,
    inStock: 0,
    maintenance: 0,
    reserved: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDevices = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await deviceService.getAllDevices({ page: 1, page_size: 100 });
      const allDevices = response.devices || [];
      
      setDevices(allDevices);
      
      // Calculate stats
      const statusCounts = {
        total: allDevices.length,
        deployed: allDevices.filter(d => d.status === 'deployed').length,
        inStock: allDevices.filter(d => d.status === 'in_stock').length,
        maintenance: allDevices.filter(d => d.status === 'maintenance').length,
        reserved: allDevices.filter(d => d.status === 'reserved').length
      };
      
      setStats(statusCounts);
    } catch (err) {
      console.error('Error fetching devices:', err);
      setError('Failed to load devices. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  const getStatusBadge = (status) => {
    return <span className={`badge badge-${status}`}>{status?.replace('_', ' ')}</span>;
  };

  const getDeviceTypeIcon = (type) => {
    const iotTypes = ['sensor', 'gateway', 'actuator', 'controller', 'iot_sensor', 'iot_gateway', 'iot_actuator'];
    if (iotTypes.includes(type)) {
      return <FiCpu className="device-icon iot" />;
    }
    return <FiCpu className="device-icon end" />;
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loader">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button className="btn btn-secondary" onClick={fetchDevices}>
          <FiRefreshCw />
          Refresh
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon total">
            <FiCpu />
          </div>
          <div className="stat-info">
            <h3>{stats.total}</h3>
            <p>Total Devices</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon deployed">
            <FiCheckCircle />
          </div>
          <div className="stat-info">
            <h3>{stats.deployed}</h3>
            <p>Deployed</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon in-stock">
            <FiPackage />
          </div>
          <div className="stat-info">
            <h3>{stats.inStock}</h3>
            <p>In Stock</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon maintenance">
            <FiTool />
          </div>
          <div className="stat-info">
            <h3>{stats.maintenance}</h3>
            <p>Maintenance</p>
          </div>
        </div>
      </div>

      {/* Recent Devices Table */}
      <div className="card">
        <div className="card-header">
          <h2>All Devices</h2>
          <span className="device-count">{devices.length} devices</span>
        </div>

        {devices.length === 0 ? (
          <div className="empty-state">
            <FiAlertCircle />
            <p>No devices found</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Device</th>
                  <th>Type</th>
                  <th>Serial Number</th>
                  <th>Status</th>
                  <th>Location</th>
                  <th>Last Updated</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {devices.map((device) => (
                  <tr key={device.id}>
                    <td>
                      <div className="device-name">
                        {getDeviceTypeIcon(device.type)}
                        <span>{device.name}</span>
                      </div>
                    </td>
                    <td>{device.type?.replace('_', ' ')}</td>
                    <td><code>{device.serial_number}</code></td>
                    <td>{getStatusBadge(device.status)}</td>
                    <td>{device.location || '-'}</td>
                    <td>{device.updated_at ? new Date(device.updated_at).toLocaleDateString() : '-'}</td>
                    <td>
                      <button 
                        className="btn btn-sm btn-track"
                        onClick={() => navigate(`/device/${device.id}`)}
                        title="Track Device"
                      >
                        <FiActivity /> Track
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
