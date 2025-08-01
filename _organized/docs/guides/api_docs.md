# API Documentation: LLaMA GPU Project

## Overview
This document provides API reference and usage examples for all major modules in the LLaMA GPU project, including backend, plugin manager, dashboard, marketplace, monitoring, and utilities.

## Modules
### Backend
- `/infer` (POST): Run inference on input data
- `/batch_infer` (POST): Batch inference
- `/stream_infer` (POST): Streaming inference
- `/health` (GET): Backend health status

### Plugin Manager
- `load_plugin(name, path)`: Dynamically load a plugin
- `unload_plugin(name)`: Unload a plugin
- `reload_plugin(name)`: Reload a plugin
- `list_plugins()`: List loaded plugins
- `get_plugin_metadata(name)`: Get plugin metadata
- `validate_plugin(name)`: Validate plugin
- `get_plugin_status(name)`: Get plugin status
- `scan_available_plugins()`: List available plugins
- `is_plugin_compatible(name, required_version)`: Check plugin version compatibility

### Dashboard (Flask UI)
- `/dashboard/plugins` (GET): List plugins
- `/dashboard/plugins/load` (POST): Load plugin
- `/dashboard/plugins/unload` (POST): Unload plugin

### Marketplace (Flask UI)
- `/marketplace/plugins` (GET): List available plugins
- `/marketplace/plugins/install` (POST): Install plugin
- `/marketplace/plugins/update` (POST): Update plugin

### Monitoring
- `/metrics` (GET): Prometheus metrics
- `/plugin_health` (GET): Plugin health status

### Utilities
- Logging, error handling, config management, role management

## Usage Examples
See module docstrings and example scripts for usage details.

## Update Log
- [2025-07-21] Initial API documentation
- [2025-07-21] Added plugin manager, dashboard, marketplace, monitoring endpoints
- [2025-07-21] Updated with recent features and endpoints
