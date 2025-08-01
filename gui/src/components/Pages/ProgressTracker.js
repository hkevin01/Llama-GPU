import {
    AlertTriangle,
    Calendar,
    Clock,
    Edit,
    Eye,
    Plus,
    Search,
    Tag,
    TrendingUp,
    User
} from 'lucide-react';
import { useState } from 'react';
import { useProject } from '../../context/ProjectContext';
import './ProgressTracker.css';

function ProgressTracker() {
  const { state, dispatch, getFilteredTasks, getProjectStats } = useProject();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('priority');
  const [sortOrder, setSortOrder] = useState('desc');

  const stats = getProjectStats();
  const tasks = getFilteredTasks();

  const filteredTasks = tasks
    .filter(task =>
      task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.assignee.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];

      if (sortBy === 'priority') {
        const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        aValue = priorityOrder[a.priority];
        bValue = priorityOrder[b.priority];
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  const handleFilterChange = (filterType, value) => {
    dispatch({
      type: 'UPDATE_FILTERS',
      payload: { [filterType]: value }
    });
  };

  const openTaskModal = (taskId, mode = 'view') => {
    dispatch({
      type: 'OPEN_TASK_MODAL',
      payload: { taskId, mode }
    });
  };

  const createNewTask = () => {
    dispatch({
      type: 'OPEN_TASK_MODAL',
      payload: { taskId: null, mode: 'create' }
    });
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'complete':
        return '✅';
      case 'progress':
        return '🟡';
      case 'blocked':
        return '❌';
      case 'review':
        return '🔄';
      default:
        return '⭕';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'critical':
        return '🔴';
      case 'high':
        return '🟠';
      case 'medium':
        return '🟡';
      default:
        return '🟢';
    }
  };

  return (
    <div className="progress-tracker animate-fadeIn">
      <div className="tracker-header">
        <div className="header-content">
          <h1 className="page-title">Progress Tracker</h1>
          <p className="page-subtitle">
            Monitor task progress and team performance across all project phases
          </p>
        </div>
        <button className="btn btn-primary" onClick={createNewTask}>
          <Plus size={16} />
          New Task
        </button>
      </div>

      {/* Progress Overview */}
      <div className="progress-overview">
        <div className="overview-card">
          <div className="overview-metric">
            <TrendingUp className="metric-icon" />
            <div className="metric-content">
              <h3>{stats.completionRate}%</h3>
              <p>Overall Progress</p>
            </div>
          </div>
        </div>
        <div className="overview-card">
          <div className="overview-metric">
            <Clock className="metric-icon" />
            <div className="metric-content">
              <h3>{stats.inProgress}</h3>
              <p>Active Tasks</p>
            </div>
          </div>
        </div>
        <div className="overview-card">
          <div className="overview-metric">
            <AlertTriangle className="metric-icon" />
            <div className="metric-content">
              <h3>{stats.blocked}</h3>
              <p>Blocked Items</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="tracker-controls">
        <div className="search-container">
          <Search className="search-icon" size={16} />
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-controls">
          <select
            value={state.ui.filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="complete">Complete</option>
            <option value="progress">In Progress</option>
            <option value="not-started">Not Started</option>
            <option value="blocked">Blocked</option>
            <option value="review">Under Review</option>
          </select>

          <select
            value={state.ui.filters.priority}
            onChange={(e) => handleFilterChange('priority', e.target.value)}
            className="filter-select"
          >
            <option value="all">All Priority</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={state.ui.filters.category}
            onChange={(e) => handleFilterChange('category', e.target.value)}
            className="filter-select"
          >
            <option value="all">All Categories</option>
            <option value="Core Development">Core Development</option>
            <option value="Frontend">Frontend</option>
            <option value="Backend">Backend</option>
            <option value="Quality Assurance">Quality Assurance</option>
            <option value="Documentation">Documentation</option>
            <option value="DevOps">DevOps</option>
            <option value="Security">Security</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="priority">Sort by Priority</option>
            <option value="progress">Sort by Progress</option>
            <option value="plannedEnd">Sort by Due Date</option>
            <option value="title">Sort by Title</option>
          </select>
        </div>
      </div>

      {/* Task List */}
      <div className="task-list">
        {filteredTasks.length === 0 ? (
          <div className="empty-state">
            <Search size={48} className="empty-icon" />
            <h3>No tasks found</h3>
            <p>Try adjusting your filters or search terms</p>
          </div>
        ) : (
          <div className="task-grid">
            {filteredTasks.map((task) => (
              <div key={task.id} className={`task-card ${task.status}`}>
                <div className="task-header">
                  <div className="task-meta">
                    <span className="task-id">{task.id}</span>
                    <div className="task-badges">
                      <span className={`status-badge status-${task.status}`}>
                        {getStatusIcon(task.status)} {task.status.replace('-', ' ')}
                      </span>
                      <span className={`priority-badge priority-${task.priority}`}>
                        {getPriorityIcon(task.priority)} {task.priority}
                      </span>
                    </div>
                  </div>
                  <div className="task-actions">
                    <button
                      className="action-btn"
                      onClick={() => openTaskModal(task.id, 'view')}
                      title="View Details"
                    >
                      <Eye size={16} />
                    </button>
                    <button
                      className="action-btn"
                      onClick={() => openTaskModal(task.id, 'edit')}
                      title="Edit Task"
                    >
                      <Edit size={16} />
                    </button>
                  </div>
                </div>

                <div className="task-content">
                  <h3 className="task-title">{task.title}</h3>
                  <p className="task-description">{task.description}</p>

                  <div className="task-details">
                    <div className="detail-item">
                      <Tag size={14} />
                      <span>{task.category}</span>
                    </div>
                    <div className="detail-item">
                      <User size={14} />
                      <span>{task.assignee}</span>
                    </div>
                    <div className="detail-item">
                      <Calendar size={14} />
                      <span>{task.plannedEnd || 'No due date'}</span>
                    </div>
                  </div>
                </div>

                <div className="task-progress">
                  <div className="progress-header">
                    <span className="progress-label">Progress</span>
                    <span className="progress-value">{task.progress}%</span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className={`progress-fill status-${task.status}`}
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                </div>

                {task.blockers && task.blockers.length > 0 && (
                  <div className="task-blockers">
                    <AlertTriangle size={14} />
                    <span>Blocked: {task.blockers.join(', ')}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="tracker-summary">
        <div className="summary-card">
          <h4>Showing {filteredTasks.length} of {tasks.length} tasks</h4>
          <div className="summary-breakdown">
            <span>Complete: {filteredTasks.filter(t => t.status === 'complete').length}</span>
            <span>In Progress: {filteredTasks.filter(t => t.status === 'progress').length}</span>
            <span>Blocked: {filteredTasks.filter(t => t.status === 'blocked').length}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProgressTracker;
