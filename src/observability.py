"""Observability module: Logging, Tracing, and Metrics."""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

import structlog


class MetricsCollector:
    """Collects metrics about agent operations."""

    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None

    def start_timer(self) -> None:
        """Start operation timer."""
        self.start_time = time.time()

    def record_metric(
        self,
        metric_name: str,
        value: Any,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a metric."""
        elapsed = (
            time.time() - self.start_time if self.start_time else None
        )
        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "metric_name": metric_name,
            "value": value,
            "elapsed_seconds": elapsed,
            "tags": tags or {},
        }
        self.metrics.append(metric)
        logging.info(f"Metric recorded: {metric_name}={value}")

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            "total_metrics": len(self.metrics),
            "metrics": self.metrics,
        }

    def save_metrics(self, filepath: str) -> None:
        """Save metrics to JSON file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.get_summary(), f, indent=2)
        logging.info(f"Metrics saved to {filepath}")


class TraceCollector:
    """Collects execution traces for debugging and analysis."""

    def __init__(self):
        self.traces: List[Dict[str, Any]] = []

    def record_trace(
        self,
        agent_name: str,
        action: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error: Optional[str] = None,
    ) -> None:
        """Record an agent action trace."""
        trace = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "action": action,
            "status": status,
            "input": input_data,
            "output": output_data,
            "error": error,
        }
        self.traces.append(trace)
        logging.debug(f"Trace: {agent_name} - {action} - {status}")

    def get_traces(self) -> List[Dict[str, Any]]:
        """Get all recorded traces."""
        return self.traces

    def save_traces(self, filepath: str) -> None:
        """Save traces to JSON file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.traces, f, indent=2)
        logging.info(f"Traces saved to {filepath}")


def setup_logging(log_level: str = "INFO") -> None:
    """Set up structured logging with structlog."""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Global instances
metrics_collector = MetricsCollector()
trace_collector = TraceCollector()
