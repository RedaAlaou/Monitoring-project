import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { deviceService } from '../services/api';
import { 
  FiCpu, FiPlus, FiRefreshCw, FiEdit2, FiTrash2, 
  FiCheckCircle, FiAlertCircle, FiX, FiSearch, FiActivity
} from 'react-icons/fi';
import './Devices.css';

// IoT device types
const IOT_TYPES = ['sensor', 'gateway', 'actuator', 'controller', 'iot_sensor', 'iot_gateway', 'iot_actuator', 'other'];

const IoTDevices = () => {
  const navigate = useNavigate();
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingDevice, setEditingDevice] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'sensor',
    serial_number: '',
    description: '',
    location: '',
    specifications: ''
  });

  const fetchDevices = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await deviceService.getAllDevices({ page: 1, page_size: 100 });
      const allDevices = response.devices || [];
      // Filter only IoT devices
      const iotDevices = allDevices.filter(d => IOT_TYPES.includes(d.type));
      setDevices(iotDevices);
    } catch (err) {
      console.error('Error fetching devices:', err);
      setError('Failed to load IoT devices.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const openCreateModal = () => {
    setEditingDevice(null);
    setFormData({
      name: '',
      type: 'sensor',
      serial_number: '',
      description: '',
      location: '',
      specifications: ''
    });
    setShowModal(true);
  };

  const openEditModal = (device) => {
    setEditingDevice(device);
    setFormData({
      name: device.name,
      type: device.type,
      serial_number: device.serial_number,
      description: device.description || '',
      location: device.location || '',
      specifications: device.specifications || ''
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingDevice(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (editingDevice) {
        await deviceService.updateDevice(editingDevice.id, {
          name: formData.name,
          description: formData.description,
          location: formData.location,
          specifications: formData.specifications
        });
        setSuccess('Device updated successfully!');
      } else {
        await deviceService.createDevice(formData);
        setSuccess('Device created successfully!');
      }
      closeModal();
      fetchDevices();
    } catch (err) {
      console.error('Error saving device:', err);
      setError(err.response?.data?.detail || 'Failed to save device.');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this device?')) return;
    
    try {
      await deviceService.deleteDevice(id);
      setSuccess('Device deleted successfully!');
      fetchDevices();
    } catch (err) {
      console.error('Error deleting device:', err);
      setError('Failed to delete device.');
    }
  };

  const handleDeploy = async (id) => {
    const location = prompt('Enter deployment location:');
    if (!location) return;

    try {
      await deviceService.deployDevice(id, { location });
      setSuccess('Device deployed successfully!');
      fetchDevices();
    } catch (err) {
      console.error('Error deploying device:', err);
      setError('Failed to deploy device.');
    }
  };

  const handleMaintenance = async (id) => {
    try {
      await deviceService.setMaintenance(id, { notes: 'Scheduled maintenance' });
      setSuccess('Device sent to maintenance!');
      fetchDevices();
    } catch (err) {
      console.error('Error setting maintenance:', err);
      setError('Failed to set maintenance.');
    }
  };

  const getStatusBadge = (status) => {
    return <span className={`badge badge-${status}`}>{status?.replace('_', ' ')}</span>;
  };

  const filteredDevices = devices.filter(d => 
    d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.serial_number.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="devices-page">
        <div className="loader">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="devices-page">
      <div className="page-header">
        <div>
          <h1><FiCpu /> IoT Devices</h1>
          <p>Manage sensors, gateways, actuators and controllers</p>
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={fetchDevices}>
            <FiRefreshCw /> Refresh
          </button>
          <button className="btn btn-primary" onClick={openCreateModal}>
            <FiPlus /> Add Device
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Search */}
      <div className="search-bar">
        <FiSearch className="search-icon" />
        <input
          type="text"
          placeholder="Search devices..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>

      {/* Devices Grid */}
      <div className="devices-grid">
        {filteredDevices.length === 0 ? (
          <div className="empty-state">
            <FiAlertCircle />
            <p>No IoT devices found</p>
            <button className="btn btn-primary" onClick={openCreateModal}>
              <FiPlus /> Add your first device
            </button>
          </div>
        ) : (
          filteredDevices.map((device) => (
            <div key={device.id} className="device-card">
              <div className="device-card-header">
                <div className="device-title">
                  <FiCpu className="device-type-icon" />
                  <div>
                    <h3>{device.name}</h3>
                    <code>{device.serial_number}</code>
                  </div>
                </div>
                {getStatusBadge(device.status)}
              </div>

              <div className="device-card-body">
                <div className="device-info-row">
                  <span className="label">Type:</span>
                  <span>{device.type?.replace('_', ' ')}</span>
                </div>
                <div className="device-info-row">
                  <span className="label">Location:</span>
                  <span>{device.location || 'Not set'}</span>
                </div>
                {device.description && (
                  <div className="device-description">
                    {device.description}
                  </div>
                )}
              </div>

              <div className="device-card-actions">
                <button className="btn-icon track" onClick={() => navigate(`/device/${device.id}`)} title="Track">
                  <FiActivity />
                </button>
                <button className="btn-icon" onClick={() => openEditModal(device)} title="Edit">
                  <FiEdit2 />
                </button>
                {device.status === 'in_stock' && (
                  <button className="btn-icon success" onClick={() => handleDeploy(device.id)} title="Deploy">
                    <FiCheckCircle />
                  </button>
                )}
                {device.status === 'deployed' && (
                  <button className="btn-icon warning" onClick={() => handleMaintenance(device.id)} title="Maintenance">
                    <FiAlertCircle />
                  </button>
                )}
                <button className="btn-icon danger" onClick={() => handleDelete(device.id)} title="Delete">
                  <FiTrash2 />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingDevice ? 'Edit Device' : 'Add New IoT Device'}</h2>
              <button className="modal-close" onClick={closeModal}>
                <FiX />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label htmlFor="name">Device Name</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    className="form-control"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                {!editingDevice && (
                  <>
                    <div className="form-group">
                      <label htmlFor="type">Device Type</label>
                      <select
                        id="type"
                        name="type"
                        className="form-control"
                        value={formData.type}
                        onChange={handleInputChange}
                        required
                      >
                        <option value="sensor">Sensor</option>
                        <option value="gateway">Gateway</option>
                        <option value="actuator">Actuator</option>
                        <option value="controller">Controller</option>
                        <option value="iot_sensor">IoT Sensor</option>
                        <option value="iot_gateway">IoT Gateway</option>
                        <option value="iot_actuator">IoT Actuator</option>
                        <option value="other">Other</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label htmlFor="serial_number">Serial Number</label>
                      <input
                        type="text"
                        id="serial_number"
                        name="serial_number"
                        className="form-control"
                        value={formData.serial_number}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                  </>
                )}

                <div className="form-group">
                  <label htmlFor="location">Location</label>
                  <input
                    type="text"
                    id="location"
                    name="location"
                    className="form-control"
                    value={formData.location}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="description">Description</label>
                  <textarea
                    id="description"
                    name="description"
                    className="form-control"
                    rows="3"
                    value={formData.description}
                    onChange={handleInputChange}
                  ></textarea>
                </div>

                <div className="form-group">
                  <label htmlFor="specifications">Specifications (JSON)</label>
                  <textarea
                    id="specifications"
                    name="specifications"
                    className="form-control"
                    rows="2"
                    placeholder='{"model": "...", "firmware": "..."}'
                    value={formData.specifications}
                    onChange={handleInputChange}
                  ></textarea>
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingDevice ? 'Update Device' : 'Create Device'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default IoTDevices;
