import React from 'react';
import { Search, Bell, User, RefreshCw } from 'lucide-react';
import { useProject } from '../../context/ProjectContext';
import './Header.css';

function Header({ onSidebarToggle }) {
  const { state, dispatch, getUnreadNotifications } = useProject();
  const unreadCount = getUnreadNotifications().length;

  const handleRefresh = () => {
    // Simulate data refresh
    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        type: 'info',
        title: 'Data Refreshed',
        message: 'Project data has been updated successfully'
      }
    });
  };

  const toggleNotifications = () => {
    dispatch({ type: 'TOGGLE_NOTIFICATIONS' });
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="search-container">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              placeholder="Search tasks, plans, or team members..."
              className="search-input"
            />
          </div>
        </div>

        <div className="header-right">
          <button 
            className="header-action refresh-btn"
            onClick={handleRefresh}
            title="Refresh Data"
          >
            <RefreshCw size={20} />
          </button>

          <button 
            className="header-action notification-btn"
            onClick={toggleNotifications}
            title="Notifications"
          >
            <Bell size={20} />
            {unreadCount > 0 && (
              <span className="notification-badge">{unreadCount}</span>
            )}
          </button>

          <div className="user-menu">
            <button className="user-button">
              <User size={20} />
              <span className="user-name">Project Manager</span>
            </button>
          </div>
        </div>
      </div>

      <div className="header-breadcrumb">
        <div className="breadcrumb-content">
          <span className="project-name">LLaMA GPU Project</span>
          <span className="breadcrumb-separator">•</span>
          <span className="current-page">Dashboard</span>
          <span className="last-updated">
            Last updated: {new Date().toLocaleString()}
          </span>
        </div>
      </div>
    </header>
  );
}

export default Header;
