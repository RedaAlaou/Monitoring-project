import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FiHome, FiCpu, FiMonitor, FiLogOut, FiUser, FiActivity } from 'react-icons/fi';
import './Layout.css';

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <FiActivity className="logo-icon" />
          <h1>IoT Monitor</h1>
        </div>
        
        <nav className="sidebar-nav">
          <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} end>
            <FiHome />
            <span>Dashboard</span>
          </NavLink>
          <NavLink to="/iot-devices" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <FiCpu />
            <span>IoT Devices</span>
          </NavLink>
          <NavLink to="/end-devices" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <FiMonitor />
            <span>End Devices</span>
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <FiUser />
            <span>{user?.email || 'User'}</span>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <FiLogOut />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
