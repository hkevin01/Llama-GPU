# Prometheus Integration & Resource Dashboards

This guide explains how to integrate Prometheus for resource monitoring in Llama-GPU and set up dashboards for real-time analytics.

## Prometheus Integration

1. **Install Prometheus**
   - Follow official docs: https://prometheus.io/docs/introduction/overview/
2. **Export Metrics**
   - Use `prometheus_client` Python package:
     ```bash
     pip install prometheus_client
     ```
   - Add metrics export to API server (see `src/api_server.py`):
     ```python
     from prometheus_client import start_http_server, Summary
     start_http_server(8001)
     REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
     @REQUEST_TIME.time
     def process_request():
         ...
     ```
3. **Configure Prometheus**
   - Add job to `prometheus.yml`:
     ```yaml
     scrape_configs:
       - job_name: 'llama-gpu'
         static_configs:
           - targets: ['localhost:8001']
     ```
4. **Visualize Metrics**
   - Use Grafana for dashboards: https://grafana.com/docs/grafana/latest/getting-started/
   - Import Prometheus data source and create resource dashboards.

## Metrics Tracked
- API request latency
- GPU/CPU/memory utilization
- Model inference time
- Error rates
- Custom business metrics

---
_Last updated: July 21, 2025_
