# Monitoring & Alerting Integration

This module integrates Prometheus for metrics and Grafana for alerting. Endpoints:
- `/metrics`: Prometheus metrics
- `/alert`: Send alert to Grafana

Setup:
- Configure Prometheus to scrape `/metrics`
- Set up Grafana to visualize metrics and receive alerts
