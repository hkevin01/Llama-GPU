# Configuration Overview: LLaMA GPU Project

## Config Files
- `plugin_manager_config.yaml`: Plugin manager settings
- `dashboard_config.yaml`: Dashboard UI settings
- `marketplace_config.yaml`: Marketplace settings
- `monitoring_config.yaml`: Monitoring and Prometheus settings

## Example: plugin_manager_config.yaml
```yaml
plugins:
  - name: example_plugin
    path: src.plugin_templates.example_plugin
    enabled: true
```

## Example: dashboard_config.yaml
```yaml
theme: dark
refresh_interval: 10
```

## Example: marketplace_config.yaml
```yaml
remote_url: https://plugins.llama-gpu.com/api/plugins
```

## Example: monitoring_config.yaml
```yaml
prometheus:
  enabled: true
  port: 9090
```

## Update Log
- [2025-07-21] Initial config documentation
- [2025-07-21] Added examples for all major config files
