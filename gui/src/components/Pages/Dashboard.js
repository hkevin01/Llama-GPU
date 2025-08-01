import { ArcElement, BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from 'chart.js';
import {
    AlertTriangle,
    Calendar,
    CheckCircle2,
    Play,
    Target
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { useProject } from '../../context/ProjectContext';
import './Dashboard.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, ArcElement);

function Dashboard() {
  const { state, getProjectStats, getFilteredTasks } = useProject();
  const [timeframe, setTimeframe] = useState('week');
  const stats = getProjectStats();
  const recentTasks = getFilteredTasks().slice(0, 5);

  // Simulated performance data
  const [performanceData, setPerformanceData] = useState({
    weekly: [78, 82, 85, 79, 88, 91, 87],
    monthly: [75, 78, 82, 85, 87, 89, 91, 88]
  });

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setPerformanceData(prev => ({
        ...prev,
        weekly: prev.weekly.map(val => Math.max(0, Math.min(100, val + (Math.random() - 0.5) * 4)))
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const statusChartData = {
    labels: ['Complete', 'In Progress', 'Not Started', 'Blocked'],
    datasets: [{
      data: [stats.completed, stats.inProgress, stats.notStarted, stats.blocked],
      backgroundColor: ['#10b981', '#f59e0b', '#6b7280', '#ef4444'],
      borderWidth: 0,
      hoverOffset: 4
    }]
  };

  const progressChartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'Progress %',
      data: performanceData[timeframe === 'week' ? 'weekly' : 'monthly'],
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      fill: true
    }]
  };

  const categoryData = {
    labels: ['Core Dev', 'Frontend', 'Backend', 'QA', 'DevOps', 'Docs'],
    datasets: [{
      label: 'Tasks',
      data: [4, 3, 2, 1, 1, 1],
      backgroundColor: [
        '#3b82f6',
        '#10b981',
        '#f59e0b',
        '#ef4444',
        '#8b5cf6',
        '#06b6d4'
      ]
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          usePointStyle: true
        }
      }
    }
  };

  return (
    <div className="dashboard animate-fadeIn">
      <div className="dashboard-header">
        <div className="header-content">
          <h1 className="page-title">Project Dashboard</h1>
          <p className="page-subtitle">
            Real-time overview of LLaMA GPU project progress and team performance
          </p>
        </div>
        <div className="header-actions">
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="timeframe-select"
          >
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon success">
            <CheckCircle2 size={24} />
          </div>
          <div className="metric-content">
            <h3 className="metric-value">{stats.completed}</h3>
            <p className="metric-label">Completed Tasks</p>
            <span className="metric-change positive">+2 this week</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon warning">
            <Play size={24} />
          </div>
          <div className="metric-content">
            <h3 className="metric-value">{stats.inProgress}</h3>
            <p className="metric-label">In Progress</p>
            <span className="metric-change neutral">Active development</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon info">
            <Target size={24} />
          </div>
          <div className="metric-content">
            <h3 className="metric-value">{stats.completionRate}%</h3>
            <p className="metric-label">Overall Progress</p>
            <span className="metric-change positive">+8% this month</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon danger">
            <AlertTriangle size={24} />
          </div>
          <div className="metric-content">
            <h3 className="metric-value">{stats.blocked}</h3>
            <p className="metric-label">Blocked Tasks</p>
            <span className="metric-change negative">Needs attention</span>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="chart-row">
          <div className="chart-card">
            <div className="chart-header">
              <h3>Progress Timeline</h3>
              <p>Daily progress tracking</p>
            </div>
            <div className="chart-container">
              <Line data={progressChartData} options={chartOptions} />
            </div>
          </div>

          <div className="chart-card">
            <div className="chart-header">
              <h3>Task Status Distribution</h3>
              <p>Current task breakdown</p>
            </div>
            <div className="chart-container">
              <Doughnut data={statusChartData} options={chartOptions} />
            </div>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <h3>Tasks by Category</h3>
            <p>Distribution across project areas</p>
          </div>
          <div className="chart-container">
            <Bar data={categoryData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Recent Activity & Upcoming */}
      <div className="activity-section">
        <div className="activity-card">
          <div className="card-header">
            <h3>Recent Activity</h3>
            <p>Latest task updates</p>
          </div>
          <div className="activity-list">
            {recentTasks.map((task, index) => (
              <div key={task.id} className="activity-item">
                <div className={`activity-dot ${task.status}`}></div>
                <div className="activity-content">
                  <h4>{task.title}</h4>
                  <p>{task.assignee} • {task.category}</p>
                  <div className="activity-meta">
                    <span className={`status-badge status-${task.status}`}>
                      {task.status.replace('-', ' ')}
                    </span>
                    <span className="activity-time">
                      {task.actualEnd || 'In progress'}
                    </span>
                  </div>
                </div>
                <div className="activity-progress">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                  <span className="progress-text">{task.progress}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="upcoming-card">
          <div className="card-header">
            <h3>Upcoming Deadlines</h3>
            <p>Next 7 days</p>
          </div>
          <div className="deadline-list">
            <div className="deadline-item urgent">
              <Calendar size={16} />
              <div className="deadline-content">
                <h4>Security Implementation Review</h4>
                <p>Due in 2 days</p>
              </div>
            </div>
            <div className="deadline-item normal">
              <Calendar size={16} />
              <div className="deadline-content">
                <h4>API Documentation Complete</h4>
                <p>Due in 5 days</p>
              </div>
            </div>
            <div className="deadline-item normal">
              <Calendar size={16} />
              <div className="deadline-content">
                <h4>Performance Testing Phase</h4>
                <p>Due in 7 days</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Team Performance */}
      <div className="team-section">
        <div className="team-card">
          <div className="card-header">
            <h3>Team Performance</h3>
            <p>Current sprint overview</p>
          </div>
          <div className="team-grid">
            <div className="team-member">
              <div className="member-avatar">DT</div>
              <div className="member-info">
                <h4>Development Team</h4>
                <p>4 active tasks</p>
                <div className="member-progress">
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: '85%' }} />
                  </div>
                  <span>85%</span>
                </div>
              </div>
            </div>
            <div className="team-member">
              <div className="member-avatar">FT</div>
              <div className="member-info">
                <h4>Frontend Team</h4>
                <p>2 active tasks</p>
                <div className="member-progress">
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: '92%' }} />
                  </div>
                  <span>92%</span>
                </div>
              </div>
            </div>
            <div className="team-member">
              <div className="member-avatar">QA</div>
              <div className="member-info">
                <h4>QA Team</h4>
                <p>3 active tasks</p>
                <div className="member-progress">
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: '70%' }} />
                  </div>
                  <span>70%</span>
                </div>
              </div>
            </div>
            <div className="team-member">
              <div className="member-avatar">ST</div>
              <div className="member-info">
                <h4>Security Team</h4>
                <p>1 active task</p>
                <div className="member-progress">
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: '0%' }} />
                  </div>
                  <span>0%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
