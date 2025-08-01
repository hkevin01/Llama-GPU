"""
Monitoring & Alerting Module
Provides alerting and anomaly detection interfaces.
"""

from typing import Any, Dict
import statistics


def send_alert(message: str) -> None:
    """
    Send an alert message (simulated).
    Logs output to logs/monitoring_alerts.log.
    """
    with open('logs/monitoring_alerts.log', 'a', encoding='utf-8') as log:
        log.write(f"Alert sent: {message}\n")


def detect_anomaly(metrics: Dict[str, Any]) -> bool:
    """
    Detect anomalies in metrics using simple z-score.
    Logs output to logs/monitoring_alerts.log.
    """
    values = list(metrics.values())
    if not values:
        return False
    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0
    anomaly = any(abs(v - mean) > 2 * stdev for v in values if stdev > 0)
    with open('logs/monitoring_alerts.log', 'a', encoding='utf-8') as log:
        log.write(f"Anomaly detection: mean={mean}, stdev={stdev}, anomaly={anomaly}\n")
    return anomaly
