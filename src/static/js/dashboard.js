/**
 * Dashboard JavaScript for LLaMA GPU
 * Handles real-time updates, API calls, and user interactions
 */

// Global variables
let socket = null;
let dashboardData = {};
let refreshInterval = null;

// Initialize dashboard
function initializeDashboard() {
    console.log('Initializing LLaMA GPU Dashboard...');

    // Start periodic refresh
    refreshInterval = setInterval(refreshDashboardData, 30000); // 30 seconds

    // Load initial data
    refreshDashboardData();

    // Setup event listeners
    setupEventListeners();
}

// Initialize WebSocket connection for real-time updates
function initializeWebSocket() {
    if (typeof io !== 'undefined') {
        socket = io();

        socket.on('connect', function() {
            console.log('WebSocket connected');
            showNotification('Connected to real-time updates', 'success');
        });

        socket.on('disconnect', function() {
            console.log('WebSocket disconnected');
            showNotification('Real-time updates disconnected', 'warning');
        });

        socket.on('system_update', function(data) {
            updateSystemMetrics(data);
        });

        socket.on('plugin_update', function(data) {
            updatePluginStatus(data);
        });

        socket.on('error_notification', function(data) {
            showNotification(data.message, 'danger');
        });
    }
}

// Setup event listeners
function setupEventListeners() {
    // Navigation active state
    updateNavigationState();

    // Auto-refresh toggle (if implemented)
    const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
    if (autoRefreshToggle) {
        autoRefreshToggle.addEventListener('change', function(e) {
            if (e.target.checked) {
                refreshInterval = setInterval(refreshDashboardData, 30000);
            } else {
                clearInterval(refreshInterval);
            }
        });
    }
}

// Refresh dashboard data
function refreshDashboard() {
    showLoading('Refreshing dashboard...');
    refreshDashboardData();
}

// Load plugin count
function loadPluginCount() {
    fetch('/plugins')
        .then(response => response.json())
        .then(data => {
            const count = data.plugins ? data.plugins.length : 0;
            updatePluginCount(count);
        })
        .catch(error => {
            console.error('Error loading plugin count:', error);
            updatePluginCount(0);
        });
}

// Update plugin count in UI
function updatePluginCount(count) {
    const elements = ['plugin-count', 'plugin-count-card'];
    elements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = count;
        }
    });

    // Update sidebar status
    const pluginStatus = document.getElementById('plugin-status');
    if (pluginStatus) {
        const icon = pluginStatus.querySelector('i');
        if (count > 0) {
            icon.className = 'bi bi-circle-fill text-success me-2';
        } else {
            icon.className = 'bi bi-circle-fill text-warning me-2';
        }
    }
}

// Refresh all dashboard data
function refreshDashboardData() {
    Promise.all([
        loadSystemMetrics(),
        loadPluginCount(),
        loadRecentActivity()
    ]).then(() => {
        hideLoading();
        showNotification('Dashboard refreshed', 'success', 2000);
    }).catch(error => {
        hideLoading();
        console.error('Error refreshing dashboard:', error);
        showNotification('Error refreshing dashboard', 'danger');
    });
}

// Load system metrics
function loadSystemMetrics() {
    return new Promise((resolve, reject) => {
        // Simulate system metrics (replace with actual API calls)
        const metrics = {
            gpu_utilization: Math.floor(Math.random() * 100),
            memory_usage: {
                used: (Math.random() * 16).toFixed(1),
                total: 16
            },
            system_status: 'online',
            backend: 'Auto-detect (CUDA)',
            uptime: formatUptime(Date.now() - (Math.random() * 86400000))
        };

        updateSystemMetrics(metrics);
        resolve(metrics);
    });
}

// Update system metrics in UI
function updateSystemMetrics(data) {
    if (data.gpu_utilization !== undefined) {
        const gpuUtil = document.getElementById('gpu-utilization');
        const gpuProgress = document.getElementById('gpu-progress');
        if (gpuUtil) gpuUtil.textContent = data.gpu_utilization + '%';
        if (gpuProgress) {
            gpuProgress.style.width = data.gpu_utilization + '%';
            gpuProgress.setAttribute('aria-valuenow', data.gpu_utilization);
        }
    }

    if (data.memory_usage) {
        const memoryUsage = document.getElementById('memory-usage');
        if (memoryUsage) {
            memoryUsage.textContent = `${data.memory_usage.used} / ${data.memory_usage.total} GB`;
        }
    }

    if (data.backend) {
        const backendInfo = document.getElementById('backend-info');
        if (backendInfo) backendInfo.textContent = data.backend;
    }

    if (data.uptime) {
        const uptime = document.getElementById('uptime');
        if (uptime) uptime.textContent = data.uptime;
    }
}

// Load recent activity
function loadRecentActivity() {
    return new Promise((resolve) => {
        // Simulate recent activity (replace with actual API calls)
        const activities = [
            {
                time: '2 minutes ago',
                message: 'Plugin "monitoring" loaded',
                type: 'success'
            },
            {
                time: '5 minutes ago',
                message: 'Model deployment started',
                type: 'info'
            },
            {
                time: '10 minutes ago',
                message: 'System startup completed',
                type: 'primary'
            }
        ];

        updateRecentActivity(activities);
        resolve(activities);
    });
}

// Update recent activity in UI
function updateRecentActivity(activities) {
    const activityContainer = document.getElementById('recent-activity');
    if (!activityContainer) return;

    activityContainer.innerHTML = '';
    activities.forEach(activity => {
        const item = document.createElement('div');
        item.className = 'list-group-item d-flex justify-content-between align-items-center';
        item.innerHTML = `
            <div>
                <small class="text-muted">${activity.time}</small><br>
                ${activity.message}
            </div>
            <span class="badge bg-${activity.type} rounded-pill">${activity.type}</span>
        `;
        activityContainer.appendChild(item);
    });
}

// Quick action functions
function runBenchmark() {
    showLoading('Running benchmark...');

    fetch('/benchmark', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        showNotification(`Benchmark completed: ${data.average_time.toFixed(2)}ms average`, 'success');
    })
    .catch(error => {
        hideLoading();
        console.error('Benchmark error:', error);
        showNotification('Benchmark failed', 'danger');
    });
}

function loadPlugin() {
    showLoadPluginModal();
}

function deployModel() {
    const modelName = prompt('Enter model name to deploy:');
    if (modelName) {
        showLoading('Deploying model...');

        const formData = new FormData();
        formData.append('model', modelName);

        fetch('/deploy', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(data => {
            hideLoading();
            showNotification(`Model ${modelName} deployment started`, 'success');
        })
        .catch(error => {
            hideLoading();
            console.error('Deployment error:', error);
            showNotification('Model deployment failed', 'danger');
        });
    }
}

function viewLogs() {
    // Open logs in new window or modal
    window.open('/logs', '_blank');
}

function refreshStatus() {
    refreshDashboardData();
}

// Utility functions
function showLoadPluginModal() {
    // This would typically show a modal dialog
    const name = prompt('Plugin name:');
    const path = prompt('Plugin path:');

    if (name && path) {
        loadPluginByPath(name, path);
    }
}

function loadPluginByPath(name, path) {
    showLoading('Loading plugin...');

    fetch('/dashboard/plugins/load', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name,
            path: path
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.loaded) {
            showNotification(`Plugin ${name} loaded successfully`, 'success');
            loadPluginCount(); // Refresh plugin count
        } else {
            showNotification(`Failed to load plugin ${name}`, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Plugin load error:', error);
        showNotification('Plugin load failed', 'danger');
    });
}

function showMarketplace() {
    // Navigate to marketplace or show marketplace modal
    window.location.href = '#marketplace';
    showNotification('Marketplace feature coming soon!', 'info');
}

function exportData() {
    showNotification('Export feature coming soon!', 'info');
}

// UI utility functions
function showLoading(message = 'Loading...') {
    // Create or show loading indicator
    let loader = document.getElementById('global-loader');
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.className = 'alert alert-info position-fixed top-0 end-0 m-3';
        loader.style.zIndex = '9999';
        loader.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(loader);
    } else {
        loader.querySelector('span').textContent = message;
        loader.style.display = 'block';
    }
}

function hideLoading() {
    const loader = document.getElementById('global-loader');
    if (loader) {
        loader.style.display = 'none';
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '10000';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }
}

function updateNavigationState() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href)) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

function formatUptime(milliseconds) {
    const seconds = Math.floor(milliseconds / 1000);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Cleanup when page unloads
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    if (socket) {
        socket.disconnect();
    }
});
