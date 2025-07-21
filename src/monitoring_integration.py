"""
Monitoring/Alerting Integration
Integrates with Prometheus for metrics and Grafana for alerts.
"""

import logging
from prometheus_client import Counter, generate_latest
from flask import Flask, Response, request
from src.utils.config_manager import ConfigManager

logging.basicConfig(filename='logs/monitoring_integration.log', level=logging.INFO)
app = Flask(__name__)

# Load monitoring configuration
config = ConfigManager().load_yaml('config/monitoring_config.yaml')

REQUEST_COUNT = Counter('request_count', 'Total API requests')

@app.route('/metrics')
def metrics():
    logging.info('Metrics endpoint accessed')
    return Response(generate_latest(), mimetype='text/plain')

@app.route('/alert', methods=['POST'])
def send_alert():
    data = request.get_json()
    message = data.get('message', '')
    logging.info('Alert sent to Grafana: %s', message)
    # In real use, integrate with Grafana webhook or alert API
    return {'status': 'alert sent', 'message': message}

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(port=5002)
