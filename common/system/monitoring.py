#!/usr/bin/env python3
"""
System Monitoring and Performance Tracking
Moved from monitoring/ → system/monitoring.py (Issue #284)

System monitoring utilities and performance tracking components.
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

# Optional psutil dependency with fallback
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

    # Create fallback psutil mock
    class MockPsutil:
        def cpu_percent(self):
            return 0.0

        def virtual_memory(self):
            class MockMemory:
                percent = 0.0
                used = 0
                available = 1024 * 1024 * 1024  # 1GB default

            return MockMemory()

        def disk_io_counters(self):
            return None

    psutil = MockPsutil()


class SystemMonitor:
    """
    System resource monitoring and performance tracking.
    """

    def __init__(self):
        self.start_time = None
        self.metrics = {}
        self.monitoring = False
        self._monitor_thread = None

    def start_monitoring(self, interval: float = 1.0):
        """
        Start system monitoring.

        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring:
            return

        self.start_time = time.time()
        self.monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, args=(interval,), daemon=True
        )
        self._monitor_thread.start()

    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)

    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                self._collect_metrics()
                time.sleep(interval)
            except Exception as e:
                # Silently continue monitoring on errors
                time.sleep(interval)

    def _collect_metrics(self):
        """Collect current system metrics."""
        current_time = time.time()

        # CPU and memory metrics with fallback
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()

            # Disk I/O if available
            disk_metrics = {}
            if PSUTIL_AVAILABLE:
                try:
                    disk_io = psutil.disk_io_counters()
                    if disk_io:
                        disk_metrics = {
                            "read_bytes": disk_io.read_bytes,
                            "write_bytes": disk_io.write_bytes,
                        }
                except:
                    pass

            self.metrics[current_time] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_available": memory.available,
                **disk_metrics,
            }
        except Exception:
            # Complete fallback with minimal metrics
            self.metrics[current_time] = {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "memory_used": 0,
                "memory_available": 1024 * 1024 * 1024,
            }

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        if not self.metrics:
            return {}

        latest_time = max(self.metrics.keys())
        return self.metrics[latest_time].copy()

    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary."""
        if not self.metrics:
            return {}

        cpu_values = [m["cpu_percent"] for m in self.metrics.values()]
        memory_values = [m["memory_percent"] for m in self.metrics.values()]

        return {
            "duration": time.time() - self.start_time if self.start_time else 0,
            "samples": len(self.metrics),
            "cpu_avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "cpu_max": max(cpu_values) if cpu_values else 0,
            "memory_avg": sum(memory_values) / len(memory_values) if memory_values else 0,
            "memory_max": max(memory_values) if memory_values else 0,
        }


class PerformanceTimer:
    """
    Context manager for timing operations.
    """

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

    def get_duration(self) -> float:
        """Get operation duration in seconds."""
        return self.duration or 0.0

    def get_duration_ms(self) -> float:
        """Get operation duration in milliseconds."""
        return (self.duration or 0.0) * 1000


# Global system monitor instance
_global_monitor = SystemMonitor()


def start_system_monitoring(interval: float = 1.0):
    """Start global system monitoring."""
    _global_monitor.start_monitoring(interval)


def stop_system_monitoring():
    """Stop global system monitoring."""
    _global_monitor.stop_monitoring()


def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics."""
    return _global_monitor.get_current_metrics()


def get_monitoring_summary() -> Dict[str, Any]:
    """Get monitoring summary."""
    return _global_monitor.get_summary()
