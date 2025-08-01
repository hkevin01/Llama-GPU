import { useContext, useState } from 'react';
import { ProjectContext } from '../../context/ProjectContext';
import './Settings.css';

function Settings() {
  const { dispatch } = useContext(ProjectContext);
  const [settings, setSettings] = useState({
    notifications: true,
    darkMode: false,
    autoRefresh: true,
    refreshInterval: 30,
    showCompleted: true,
    defaultView: 'dashboard'
  });

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const saveSettings = () => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: settings });
    alert('Settings saved successfully!');
  };

  return (
    <div className="settings animate-fadeIn">
      <div className="page-header">
        <h1>Settings</h1>
        <p>Customize your project tracker experience</p>
      </div>

      <div className="settings-container">
        <div className="settings-section">
          <h2>General</h2>
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.notifications}
                onChange={(e) => handleSettingChange('notifications', e.target.checked)}
              />
              Enable notifications
            </label>
          </div>

          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.darkMode}
                onChange={(e) => handleSettingChange('darkMode', e.target.checked)}
              />
              Dark mode
            </label>
          </div>

          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.autoRefresh}
                onChange={(e) => handleSettingChange('autoRefresh', e.target.checked)}
              />
              Auto-refresh data
            </label>
          </div>

          <div className="setting-item">
            <label>
              Refresh interval (seconds):
              <select
                value={settings.refreshInterval}
                onChange={(e) => handleSettingChange('refreshInterval', parseInt(e.target.value))}
              >
                <option value={15}>15</option>
                <option value={30}>30</option>
                <option value={60}>60</option>
                <option value={120}>120</option>
              </select>
            </label>
          </div>
        </div>

        <div className="settings-section">
          <h2>Display</h2>
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.showCompleted}
                onChange={(e) => handleSettingChange('showCompleted', e.target.checked)}
              />
              Show completed tasks
            </label>
          </div>

          <div className="setting-item">
            <label>
              Default view:
              <select
                value={settings.defaultView}
                onChange={(e) => handleSettingChange('defaultView', e.target.value)}
              >
                <option value="dashboard">Dashboard</option>
                <option value="progress">Progress Tracker</option>
                <option value="plans">Project Plans</option>
              </select>
            </label>
          </div>
        </div>

        <div className="settings-actions">
          <button className="btn btn-primary" onClick={saveSettings}>
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}

export default Settings;
