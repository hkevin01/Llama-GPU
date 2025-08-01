/**
 * Plugin Management JavaScript for LLaMA GPU
 * Handles plugin loading, unloading, and management
 */

// Global variables
let loadedPlugins = [];
let availablePlugins = [];

// Load list of currently loaded plugins
function loadPluginsList() {
    showLoading('Loading plugins...');

    fetch('/plugins')
        .then(response => response.json())
        .then(data => {
            loadedPlugins = data.plugins || [];
            updateLoadedPluginsTable();
            updatePluginCounts();
            hideLoading();
        })
        .catch(error => {
            console.error('Error loading plugins:', error);
            showError('Failed to load plugins list');
            hideLoading();
        });
}

// Load list of available plugins
function loadAvailablePlugins() {
    // For now, simulate available plugins
    // In a real implementation, this would call an API endpoint
    availablePlugins = [
        {
            name: 'data_processor',
            version: '1.2.0',
            description: 'Advanced data processing plugin with ML pipelines',
            status: 'available'
        },
        {
            name: 'custom_auth',
            version: '0.9.1',
            description: 'Custom authentication and authorization module',
            status: 'available'
        },
        {
            name: 'monitoring_advanced',
            version: '2.1.0',
            description: 'Advanced monitoring with Prometheus integration',
            status: 'available'
        }
    ];

    updateAvailablePluginsTable();
    updatePluginCounts();
}

// Update loaded plugins table
function updateLoadedPluginsTable() {
    const tbody = document.getElementById('loaded-plugins-tbody');
    if (!tbody) return;

    if (loadedPlugins.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    <i class="bi bi-info-circle me-2"></i>
                    No plugins currently loaded
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';
    loadedPlugins.forEach(plugin => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <strong>${plugin.name || plugin}</strong>
            </td>
            <td>
                <span class="plugin-status active">
                    <i class="bi bi-play-circle me-1"></i>Active
                </span>
            </td>
            <td>1.0.0</td>
            <td>Plugin loaded via plugin manager</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-outline-info" onclick="showPluginDetails('${plugin.name || plugin}')">
                        <i class="bi bi-info-circle"></i>
                    </button>
                    <button type="button" class="btn btn-outline-warning" onclick="reloadPlugin('${plugin.name || plugin}')">
                        <i class="bi bi-arrow-clockwise"></i>
                    </button>
                    <button type="button" class="btn btn-outline-danger" onclick="unloadPlugin('${plugin.name || plugin}')">
                        <i class="bi bi-x-circle"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Update available plugins table
function updateAvailablePluginsTable() {
    const tbody = document.getElementById('available-plugins-tbody');
    if (!tbody) return;

    if (availablePlugins.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    <i class="bi bi-info-circle me-2"></i>
                    No plugins available for installation
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';
    availablePlugins.forEach(plugin => {
        const isLoaded = loadedPlugins.some(loaded =>
            (loaded.name || loaded) === plugin.name
        );

        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${plugin.name}</strong></td>
            <td>
                <span class="badge bg-secondary">${plugin.version}</span>
            </td>
            <td>${plugin.description}</td>
            <td>
                ${isLoaded ?
                    '<span class="plugin-status active"><i class="bi bi-check-circle me-1"></i>Loaded</span>' :
                    '<span class="plugin-status"><i class="bi bi-download me-1"></i>Available</span>'
                }
            </td>
            <td>
                ${isLoaded ?
                    '<button type="button" class="btn btn-sm btn-secondary" disabled>Already Loaded</button>' :
                    `<button type="button" class="btn btn-sm btn-primary" onclick="installPlugin('${plugin.name}')">
                        <i class="bi bi-download me-1"></i>Install
                    </button>`
                }
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Update plugin counts in status cards
function updatePluginCounts() {
    const activeCount = loadedPlugins.length;
    const availableCount = availablePlugins.length;

    const activeElement = document.getElementById('active-plugins-count');
    const availableElement = document.getElementById('available-plugins-count');

    if (activeElement) activeElement.textContent = activeCount;
    if (availableElement) availableElement.textContent = availableCount;

    // Update events count (placeholder)
    const eventsElement = document.getElementById('plugin-events-count');
    if (eventsElement) eventsElement.textContent = Math.floor(Math.random() * 10);

    // Update errors count (placeholder)
    const errorsElement = document.getElementById('plugin-errors-count');
    if (errorsElement) errorsElement.textContent = 0;
}

// Show load plugin modal
function showLoadPluginModal() {
    const modal = new bootstrap.Modal(document.getElementById('loadPluginModal'));
    modal.show();
}

// Handle load plugin form submission
function loadPluginSubmit() {
    const name = document.getElementById('plugin-name').value.trim();
    const path = document.getElementById('plugin-path').value.trim();

    if (!name || !path) {
        showError('Please fill in all fields');
        return;
    }

    loadPluginByPath(name, path);

    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('loadPluginModal'));
    modal.hide();

    // Clear form
    document.getElementById('load-plugin-form').reset();
}

// Load plugin by name and path
function loadPluginByPath(name, path) {
    showLoading(`Loading plugin ${name}...`);

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
            showSuccess(`Plugin ${name} loaded successfully`);
            loadPluginsList(); // Refresh the list
        } else {
            showError(`Failed to load plugin ${name}`);
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Plugin load error:', error);
        showError(`Error loading plugin ${name}: ${error.message}`);
    });
}

// Unload a plugin
function unloadPlugin(name) {
    if (!confirm(`Are you sure you want to unload plugin "${name}"?`)) {
        return;
    }

    showLoading(`Unloading plugin ${name}...`);

    fetch('/dashboard/plugins/unload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.unloaded) {
            showSuccess(`Plugin ${name} unloaded successfully`);
            loadPluginsList(); // Refresh the list
        } else {
            showError(`Failed to unload plugin ${name}`);
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Plugin unload error:', error);
        showError(`Error unloading plugin ${name}: ${error.message}`);
    });
}

// Reload a plugin
function reloadPlugin(name) {
    showLoading(`Reloading plugin ${name}...`);

    // First unload, then load again
    fetch('/dashboard/plugins/unload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.unloaded) {
            // Find original path (this would need to be stored)
            const path = `plugins.${name}`; // Default assumption
            return loadPluginByPath(name, path);
        } else {
            throw new Error('Failed to unload plugin for reload');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Plugin reload error:', error);
        showError(`Error reloading plugin ${name}: ${error.message}`);
    });
}

// Install a plugin from available list
function installPlugin(name) {
    const plugin = availablePlugins.find(p => p.name === name);
    if (!plugin) {
        showError('Plugin not found');
        return;
    }

    // For demonstration, we'll load it with a default path
    const path = `plugins.${name}`;
    loadPluginByPath(name, path);
}

// Show plugin details modal
function showPluginDetails(name) {
    const modal = new bootstrap.Modal(document.getElementById('pluginDetailsModal'));

    // Load plugin details
    const content = document.getElementById('plugin-details-content');
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Plugin Information</h6>
                <table class="table table-borderless">
                    <tr><td><strong>Name:</strong></td><td>${name}</td></tr>
                    <tr><td><strong>Version:</strong></td><td>1.0.0</td></tr>
                    <tr><td><strong>Status:</strong></td><td><span class="plugin-status active">Active</span></td></tr>
                    <tr><td><strong>Type:</strong></td><td>System Plugin</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6>Plugin Metadata</h6>
                <table class="table table-borderless">
                    <tr><td><strong>Loaded:</strong></td><td>2 minutes ago</td></tr>
                    <tr><td><strong>Memory:</strong></td><td>~2.1 MB</td></tr>
                    <tr><td><strong>Events:</strong></td><td>5</td></tr>
                    <tr><td><strong>Dependencies:</strong></td><td>None</td></tr>
                </table>
            </div>
        </div>
        <div class="row mt-3">
            <div class="col-12">
                <h6>Description</h6>
                <p>This plugin provides core functionality for the LLaMA GPU system. It manages plugin lifecycle and provides event handling capabilities.</p>
            </div>
        </div>
    `;

    modal.show();
}

// Refresh plugins list
function refreshPlugins() {
    showLoading('Refreshing plugins...');
    Promise.all([
        loadPluginsList(),
        loadAvailablePlugins()
    ]).then(() => {
        hideLoading();
        showSuccess('Plugins refreshed successfully');
    }).catch(error => {
        hideLoading();
        showError('Failed to refresh plugins');
    });
}

// Utility functions
function showLoading(message) {
    // Use the global loading function from dashboard.js
    if (typeof window.showLoading === 'function') {
        window.showLoading(message);
    } else {
        console.log('Loading:', message);
    }
}

function hideLoading() {
    // Use the global hideLoading function from dashboard.js
    if (typeof window.hideLoading === 'function') {
        window.hideLoading();
    }
}

function showSuccess(message) {
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, 'success');
    } else {
        alert(message);
    }
}

function showError(message) {
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, 'danger');
    } else {
        alert('Error: ' + message);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Plugin-specific initialization
    console.log('Plugin management initialized');
});
