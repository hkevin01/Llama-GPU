import {
    BarChart3,
    CheckSquare,
    FileText,
    GitCompare,
    Home,
    Menu,
    Settings,
    X,
    Zap
} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Project Plans', href: '/plans', icon: FileText },
  { name: 'Progress Tracker', href: '/progress', icon: CheckSquare },
  { name: 'Plan Comparison', href: '/comparison', icon: GitCompare },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
];

function Sidebar({ collapsed, onToggle }) {
  const location = useLocation();

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-brand">
          {!collapsed && (
            <>
              <Zap className="brand-icon" />
              <span className="brand-text">LLaMA GPU</span>
            </>
          )}
          <button
            className="sidebar-toggle"
            onClick={onToggle}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <Menu size={20} /> : <X size={20} />}
          </button>
        </div>
      </div>

      <nav className="sidebar-nav">
        <ul className="nav-list">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href ||
              (item.href === '/dashboard' && location.pathname === '/');

            return (
              <li key={item.name} className="nav-item">
                <Link
                  to={item.href}
                  className={`nav-link ${isActive ? 'active' : ''}`}
                  title={collapsed ? item.name : ''}
                >
                  <item.icon className="nav-icon" size={20} />
                  {!collapsed && (
                    <span className="nav-text">{item.name}</span>
                  )}
                  {isActive && <div className="active-indicator" />}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="sidebar-footer">
        {!collapsed && (
          <div className="project-status">
            <div className="status-header">
              <h4>Project Status</h4>
            </div>
            <div className="status-metric">
              <span className="metric-label">Overall Progress</span>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: '78%' }} />
              </div>
              <span className="metric-value">78%</span>
            </div>
            <div className="status-badges">
              <div className="status-badge status-complete">
                <span>7 Complete</span>
              </div>
              <div className="status-badge status-progress">
                <span>3 In Progress</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Sidebar;
