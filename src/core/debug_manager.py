"""Centralized debug and monitoring manager for Llama-GPU."""

import time
from collections import defaultdict
from typing import Any, Dict, Optional

from src.core.logging_config import setup_logging
from src.utils.config_manager import ConfigManager

logger = setup_logging(service_name="debug-manager")


class DebugManager:
    """Centralized debug and monitoring manager for Llama-GPU.

    Provides:
    - Request tracking and metrics
    - Performance monitoring
    - Centralized logging
    - Error tracking
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the debug manager.

        Args:
            config_path: Optional path to debug config file
        """
        self.metrics = defaultdict(dict)
        self.error_counts = defaultdict(int)
        self.active_requests = {}
        self.load_config(config_path)
        self.start_time = time.time()

    def load_config(self, config_path: Optional[str] = None) -> None:
        """Load debug configuration from file.

        Args:
            config_path: Path to config file
        """
        try:
            if config_path:
                config_manager = ConfigManager()
                self.config = config_manager.load_yaml(config_path)
                logger.info("Loaded debug config from %s", config_path)
            else:
                self.config = {
                    "log_level": "INFO",
                    "metrics_enabled": True,
                    "error_tracking_enabled": True,
                    "performance_monitoring_enabled": True
                }
                logger.info("Using default debug configuration")
        except (IOError, ValueError) as e:
            logger.error("Failed to load debug config: %s", str(e))
            self.config = {}

    def start_request(
            self,
            request_id: str,
            operation: str,
            metadata: Optional[Dict] = None
    ) -> None:
        """Start tracking a new request.

        Args:
            request_id: Unique request identifier
            operation: Operation being performed
            metadata: Optional request metadata
        """
        self.active_requests[request_id] = {
            "operation": operation,
            "start_time": time.time(),
            "metadata": metadata or {}
        }
        logger.info(
            "Starting request %s: operation=%s metadata=%s",
            request_id,
            operation,
            metadata
        )

    def end_request(self, request_id: str, status: str = "success") -> None:
        """End tracking for a request.

        Args:
            request_id: Request identifier
            status: Request completion status
        """
        if request_id not in self.active_requests:
            logger.warning("Attempt to end unknown request: %s", request_id)
            return

        end_time = time.time()
        request = self.active_requests.pop(request_id)
        duration = end_time - request["start_time"]

        self.metrics[request["operation"]][request_id] = {
            "duration": duration,
            "timestamp": end_time,
            "status": status,
            "metadata": request["metadata"]
        }

        logger.info(
            "Request %s completed: operation=%s duration=%.2fs status=%s",
            request_id,
            request["operation"],
            duration,
            status
        )

    def track_error(
        self,
        error_type: str,
        details: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Track an error occurrence.

        Args:
            error_type: Type/category of error
            details: Error details/message
            metadata: Optional error context
        """
        self.error_counts[error_type] += 1
        logger.error(
            "Error occurred: type=%s count=%d details=%s metadata=%s",
            error_type,
            self.error_counts[error_type],
            details,
            metadata
        )

    def get_metrics(self, operation: Optional[str] = None) -> Dict:
        """Get collected metrics.

        Args:
            operation: Optional operation to filter metrics

        Returns:
            Dict containing metrics
        """
        if operation:
            metrics = self.metrics.get(operation, {})
        else:
            metrics = dict(self.metrics)

        # Calculate summary statistics
        summary = {
            "total_requests": len(self.metrics),
            "active_requests": len(self.active_requests),
            "error_counts": dict(self.error_counts),
            "uptime": time.time() - self.start_time
        }

        return {
            "metrics": metrics,
            "summary": summary
        }

    def get_active_requests(self) -> Dict:
        """Get currently active requests.

        Returns:
            Dict of active requests and their details
        """
        return dict(self.active_requests)

    def monitor_performance(self) -> Dict[str, Any]:
        """Get performance monitoring data.

        Returns:
            Dict containing performance metrics
        """
        metrics = {}

        # Calculate average request durations by operation
        duration_by_op = defaultdict(list)
        for op, requests in self.metrics.items():
            for req in requests.values():
                duration_by_op[op].append(req["duration"])

        metrics["average_durations"] = {
            op: sum(durations) / len(durations)
            for op, durations in duration_by_op.items()
        }

        # Calculate error rates
        total_requests = sum(len(reqs) for reqs in self.metrics.values())
        metrics["error_rates"] = {
            error_type: count / total_requests if total_requests else 0
            for error_type, count in self.error_counts.items()
        }

        return metrics
