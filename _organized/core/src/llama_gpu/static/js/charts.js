/**
 * Charts JavaScript for LLaMA GPU Dashboard
 * Handles Chart.js visualizations and real-time data updates
 */

// Global chart instances
let performanceChart = null;
let resourceChart = null;
let pluginChart = null;

// Chart configuration
const chartConfig = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'top'
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(0, 0, 0, 0.1)'
            }
        },
        x: {
            grid: {
                color: 'rgba(0, 0, 0, 0.1)'
            }
        }
    }
};

// Initialize performance chart
function initializePerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;

    const data = {
        labels: generateTimeLabels(10),
        datasets: [
            {
                label: 'GPU Utilization (%)',
                data: generateRandomData(10, 0, 100),
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            },
            {
                label: 'Memory Usage (%)',
                data: generateRandomData(10, 0, 100),
                borderColor: '#1cc88a',
                backgroundColor: 'rgba(28, 200, 138, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            },
            {
                label: 'CPU Usage (%)',
                data: generateRandomData(10, 0, 100),
                borderColor: '#36b9cc',
                backgroundColor: 'rgba(54, 185, 204, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }
        ]
    };

    performanceChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            ...chartConfig,
            plugins: {
                ...chartConfig.plugins,
                title: {
                    display: true,
                    text: 'Real-time Performance Metrics'
                }
            },
            scales: {
                ...chartConfig.scales,
                y: {
                    ...chartConfig.scales.y,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });

    // Start real-time updates
    startPerformanceUpdates();
}

// Initialize resource usage chart
function initializeResourceChart() {
    const ctx = document.getElementById('resourceChart');
    if (!ctx) return;

    const data = {
        labels: ['GPU Memory', 'System Memory', 'Storage', 'Network'],
        datasets: [{
            label: 'Usage (%)',
            data: [65, 45, 30, 15],
            backgroundColor: [
                '#4e73df',
                '#1cc88a',
                '#36b9cc',
                '#f6c23e'
            ],
            borderWidth: 0
        }]
    };

    resourceChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                title: {
                    display: true,
                    text: 'Resource Utilization'
                }
            }
        }
    });
}

// Initialize plugin activity chart
function initializePluginChart() {
    const ctx = document.getElementById('pluginChart');
    if (!ctx) return;

    const data = {
        labels: ['Active', 'Inactive', 'Loading', 'Error'],
        datasets: [{
            label: 'Plugin Status',
            data: [3, 1, 0, 0],
            backgroundColor: [
                '#1cc88a',
                '#e74a3b',
                '#36b9cc',
                '#f6c23e'
            ],
            borderWidth: 2,
            borderColor: '#fff'
        }]
    };

    pluginChart = new Chart(ctx, {
        type: 'pie',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Plugin Status Distribution'
                }
            }
        }
    });
}

// Start real-time performance updates
function startPerformanceUpdates() {
    if (!performanceChart) return;

    setInterval(() => {
        updatePerformanceChart();
    }, 5000); // Update every 5 seconds
}

// Update performance chart with new data
function updatePerformanceChart() {
    if (!performanceChart) return;

    const chart = performanceChart;
    const now = new Date();
    const timeLabel = now.toLocaleTimeString();

    // Add new data point
    chart.data.labels.push(timeLabel);
    chart.data.datasets.forEach(dataset => {
        let newValue;
        if (dataset.label.includes('GPU')) {
            newValue = Math.random() * 100;
        } else if (dataset.label.includes('Memory')) {
            newValue = 30 + Math.random() * 40; // More stable memory usage
        } else {
            newValue = 10 + Math.random() * 30; // Lower CPU usage
        }
        dataset.data.push(newValue);
    });

    // Remove old data (keep last 20 points)
    if (chart.data.labels.length > 20) {
        chart.data.labels.shift();
        chart.data.datasets.forEach(dataset => {
            dataset.data.shift();
        });
    }

    chart.update('none'); // Update without animation for real-time feel
}

// Update resource chart with new data
function updateResourceChart(data) {
    if (!resourceChart) return;

    if (data.gpu_memory !== undefined) {
        resourceChart.data.datasets[0].data[0] = data.gpu_memory;
    }
    if (data.system_memory !== undefined) {
        resourceChart.data.datasets[0].data[1] = data.system_memory;
    }
    if (data.storage !== undefined) {
        resourceChart.data.datasets[0].data[2] = data.storage;
    }
    if (data.network !== undefined) {
        resourceChart.data.datasets[0].data[3] = data.network;
    }

    resourceChart.update();
}

// Update plugin chart with new data
function updatePluginChart(data) {
    if (!pluginChart) return;

    pluginChart.data.datasets[0].data = [
        data.active || 0,
        data.inactive || 0,
        data.loading || 0,
        data.error || 0
    ];

    pluginChart.update();
}

// Create a mini chart for dashboard cards
function createMiniChart(canvasId, data, color = '#4e73df') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: generateTimeLabels(7),
            datasets: [{
                data: data,
                borderColor: color,
                backgroundColor: color + '20',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    display: false
                }
            },
            elements: {
                line: {
                    tension: 0.4
                }
            }
        }
    });
}

// Utility functions
function generateTimeLabels(count) {
    const labels = [];
    const now = new Date();

    for (let i = count - 1; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 30000); // 30 second intervals
        labels.push(time.toLocaleTimeString());
    }

    return labels;
}

function generateRandomData(count, min = 0, max = 100) {
    const data = [];
    for (let i = 0; i < count; i++) {
        data.push(Math.floor(Math.random() * (max - min + 1)) + min);
    }
    return data;
}

// Export chart data
function exportChart(chartName = 'performance') {
    let chart = null;
    let filename = 'chart-data.csv';

    switch (chartName) {
        case 'performance':
            chart = performanceChart;
            filename = 'performance-data.csv';
            break;
        case 'resource':
            chart = resourceChart;
            filename = 'resource-data.csv';
            break;
        case 'plugin':
            chart = pluginChart;
            filename = 'plugin-data.csv';
            break;
    }

    if (!chart) {
        console.error('Chart not found:', chartName);
        return;
    }

    // Convert chart data to CSV
    const csv = chartToCSV(chart);
    downloadCSV(csv, filename);
}

// Convert chart data to CSV format
function chartToCSV(chart) {
    const data = chart.data;
    let csv = '';

    // Headers
    csv += 'Time/Label';
    data.datasets.forEach(dataset => {
        csv += ',' + dataset.label;
    });
    csv += '\n';

    // Data rows
    data.labels.forEach((label, index) => {
        csv += label;
        data.datasets.forEach(dataset => {
            csv += ',' + (dataset.data[index] || '');
        });
        csv += '\n';
    });

    return csv;
}

// Download CSV file
function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Refresh chart data
function refreshChart(chartName = 'performance') {
    switch (chartName) {
        case 'performance':
            if (performanceChart) {
                updatePerformanceChart();
            }
            break;
        case 'resource':
            if (resourceChart) {
                // Simulate new resource data
                updateResourceChart({
                    gpu_memory: Math.random() * 100,
                    system_memory: Math.random() * 100,
                    storage: Math.random() * 100,
                    network: Math.random() * 100
                });
            }
            break;
        case 'plugin':
            if (pluginChart) {
                // Update with current plugin data
                if (typeof loadPluginCount === 'function') {
                    loadPluginCount();
                }
            }
            break;
    }
}

// Initialize all charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Small delay to ensure Chart.js is loaded
    setTimeout(() => {
        initializePerformanceChart();
        initializeResourceChart();
        initializePluginChart();
    }, 100);
});

// Cleanup when page unloads
window.addEventListener('beforeunload', function() {
    if (performanceChart) performanceChart.destroy();
    if (resourceChart) resourceChart.destroy();
    if (pluginChart) pluginChart.destroy();
});
