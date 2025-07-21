import pytest
from src.monitoring_alerts import send_alert, detect_anomaly

def test_send_alert_logs():
    send_alert('test_alert')
    with open('logs/monitoring_alerts.log') as log:
        assert 'Alert sent: test_alert' in log.read()

def test_detect_anomaly_logs():
    assert not detect_anomaly({'metric': 1})
    with open('logs/monitoring_alerts.log') as log:
        assert 'Anomaly detection called' in log.read()
