#!/usr/bin/env python3
"""
Agent Execution Monitoring System

Tracks agent performance, error patterns, and execution metrics for Issue #180.
Foundation for HRBP review mechanism (Issue #167).
"""
import json
import logging
import os
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ErrorCategory(Enum):
    """Error categorization for systematic analysis."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExecutionResult(Enum):
    """Execution result status."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    RETRY = "retry"


@dataclass
class ExecutionLog:
    """Execution log entry structure."""

    timestamp: str
    agent_type: str
    task_description: str
    execution_result: str
    error_category: Optional[str]
    execution_time_ms: int
    retry_count: int
    environment_state: Dict[str, Any]
    error_message: Optional[str]
    stack_trace: Optional[str]
    command: Optional[str] = None
    working_directory: Optional[str] = None


class ExecutionMonitor:
    """
    Agent Execution Monitoring System.

    Provides real-time tracking of all agent executions with:
    - Success/failure logging
    - Error categorization
    - Performance metrics
    - Environment state capture
    - Historical trend analysis
    """

    def __init__(self, log_directory: Optional[Path] = None):
        """Initialize execution monitor."""
        if log_directory is None:
            # Use centralized DirectoryManager for SSOT compliance
            from .directory_manager import directory_manager

            self.log_directory = directory_manager.get_logs_path()
        else:
            self.log_directory = Path(log_directory)

        self.log_directory.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Performance metrics
        self._start_time = None
        self._retry_count = 0

    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.log_directory / "execution_monitor.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

        self.logger = logging.getLogger(__name__)

    def start_execution(
        self, agent_type: str, task_description: str, command: Optional[str] = None
    ):
        """Start tracking an execution."""
        self._start_time = time.time()
        self._retry_count = 0
        self._agent_type = agent_type
        self._task_description = task_description
        self._command = command

        self.logger.info(f"Starting execution: {agent_type} - {task_description}")

    def increment_retry(self):
        """Increment retry counter."""
        self._retry_count += 1
        self.logger.warning(f"Retry attempt #{self._retry_count} for {self._agent_type}")

    def _categorize_error(
        self, error_message: str, stack_trace: Optional[str] = None
    ) -> ErrorCategory:
        """Automatically categorize errors based on patterns."""
        if not error_message:
            return ErrorCategory.LOW

        error_lower = error_message.lower()

        # Critical errors
        critical_patterns = [
            "segmentation fault",
            "memory error",
            "system error",
            "corrupted",
            "database connection lost",
            "disk full",
            "permission denied",
            "authentication failed",
        ]

        if any(pattern in error_lower for pattern in critical_patterns):
            return ErrorCategory.CRITICAL

        # High priority errors
        high_patterns = [
            "import error",
            "module not found",
            "file not found",
            "network error",
            "timeout",
            "connection refused",
            "invalid configuration",
        ]

        if any(pattern in error_lower for pattern in high_patterns):
            return ErrorCategory.HIGH

        # Medium priority errors
        medium_patterns = [
            "warning",
            "deprecated",
            "invalid input",
            "parsing error",
            "format error",
        ]

        if any(pattern in error_lower for pattern in medium_patterns):
            return ErrorCategory.MEDIUM

        # Default to low priority
        return ErrorCategory.LOW

    def _get_environment_state(self) -> Dict[str, Any]:
        """Capture current environment state."""
        return {
            "working_directory": str(Path.cwd()),
            "python_version": os.sys.version,
            "environment_variables": dict(os.environ),
            "timestamp": datetime.now().isoformat(),
            "process_id": os.getpid(),
        }

    def log_execution(
        self,
        result: ExecutionResult,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionLog:
        """
        Log execution outcome with comprehensive metrics.

        Args:
            result: Execution result status
            error_message: Error message if failed
            stack_trace: Stack trace if available
            additional_context: Additional context data

        Returns:
            ExecutionLog: The logged execution entry
        """
        if not hasattr(self, "_start_time") or self._start_time is None:
            self.logger.error("Execution not started - call start_execution() first")
            return None

        # Calculate execution time
        execution_time_ms = int((time.time() - self._start_time) * 1000)

        # Categorize error if present
        error_category = None
        if error_message:
            error_category = self._categorize_error(error_message, stack_trace).value

        # Create log entry
        log_entry = ExecutionLog(
            timestamp=datetime.now().isoformat(),
            agent_type=getattr(self, "_agent_type", "unknown"),
            task_description=getattr(self, "_task_description", "unknown"),
            execution_result=result.value,
            error_category=error_category,
            execution_time_ms=execution_time_ms,
            retry_count=self._retry_count,
            environment_state=self._get_environment_state(),
            error_message=error_message,
            stack_trace=stack_trace,
            command=getattr(self, "_command", None),
            working_directory=str(Path.cwd()),
        )

        # Save to file
        self._save_log_entry(log_entry)

        # Log to console
        if result == ExecutionResult.SUCCESS:
            self.logger.info(f"✅ Execution completed: {execution_time_ms}ms")
        else:
            self.logger.error(f"❌ Execution failed: {error_message} (Category: {error_category})")

        # Reset state
        self._start_time = None

        return log_entry

    def _save_log_entry(self, log_entry: ExecutionLog):
        """Save log entry to JSON file."""
        # Create daily log files
        log_date = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_directory / f"execution_logs_{log_date}.json"

        # Load existing logs or create new list
        logs = []
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                self.logger.warning(f"Could not parse existing log file: {log_file}")
                logs = []

        # Add new log entry
        logs.append(asdict(log_entry))

        # Save updated logs
        try:
            with open(log_file, "w") as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save log entry: {e}")

    def get_execution_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Get execution statistics for the last N days.

        Args:
            days: Number of days to analyze

        Returns:
            Dict with execution statistics
        """
        stats = {
            "total_executions": 0,
            "success_count": 0,
            "failure_count": 0,
            "average_execution_time_ms": 0,
            "error_categories": {},
            "agent_performance": {},
            "retry_patterns": {},
        }

        # Collect logs from the last N days
        all_logs = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            log_date = date.strftime("%Y-%m-%d")
            log_file = self.log_directory / f"execution_logs_{log_date}.json"

            if log_file.exists():
                try:
                    with open(log_file, "r") as f:
                        daily_logs = json.load(f)
                        all_logs.extend(daily_logs)
                except json.JSONDecodeError:
                    continue

        if not all_logs:
            return stats

        # Calculate statistics
        stats["total_executions"] = len(all_logs)
        execution_times = []

        for log in all_logs:
            if log["execution_result"] == "success":
                stats["success_count"] += 1
            else:
                stats["failure_count"] += 1

            execution_times.append(log["execution_time_ms"])

            # Error category stats
            if log["error_category"]:
                category = log["error_category"]
                stats["error_categories"][category] = stats["error_categories"].get(category, 0) + 1

            # Agent performance stats
            agent = log["agent_type"]
            if agent not in stats["agent_performance"]:
                stats["agent_performance"][agent] = {"total": 0, "success": 0, "failure": 0}

            stats["agent_performance"][agent]["total"] += 1
            if log["execution_result"] == "success":
                stats["agent_performance"][agent]["success"] += 1
            else:
                stats["agent_performance"][agent]["failure"] += 1

            # Retry patterns
            retry_count = log["retry_count"]
            if retry_count > 0:
                stats["retry_patterns"][retry_count] = (
                    stats["retry_patterns"].get(retry_count, 0) + 1
                )

        # Calculate average execution time
        if execution_times:
            stats["average_execution_time_ms"] = sum(execution_times) / len(execution_times)

        # Calculate success rate
        stats["success_rate"] = (
            stats["success_count"] / stats["total_executions"]
            if stats["total_executions"] > 0
            else 0
        )

        return stats


# Global monitor instance
_global_monitor = None


def get_monitor() -> ExecutionMonitor:
    """Get global monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ExecutionMonitor()
    return _global_monitor


def monitor_execution(agent_type: str, task_description: str, command: Optional[str] = None):
    """
    Decorator for monitoring function execution.

    Usage:
        @monitor_execution("p3-command", "build m7")
        def build_command():
            # command logic here
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_monitor()
            monitor.start_execution(agent_type, task_description, command)

            try:
                result = func(*args, **kwargs)
                monitor.log_execution(ExecutionResult.SUCCESS)
                return result
            except Exception as e:
                stack_trace = traceback.format_exc()
                monitor.log_execution(
                    ExecutionResult.FAILURE, error_message=str(e), stack_trace=stack_trace
                )
                raise

        return wrapper

    return decorator


# Convenience functions for external use
def log_success(agent_type: str, task_description: str, execution_time_ms: int = 0):
    """Log successful execution."""
    monitor = get_monitor()
    monitor.start_execution(agent_type, task_description)
    monitor._start_time = time.time() - (execution_time_ms / 1000)
    monitor.log_execution(ExecutionResult.SUCCESS)


def log_failure(
    agent_type: str, task_description: str, error_message: str, execution_time_ms: int = 0
):
    """Log failed execution."""
    monitor = get_monitor()
    monitor.start_execution(agent_type, task_description)
    monitor._start_time = time.time() - (execution_time_ms / 1000)
    monitor.log_execution(ExecutionResult.FAILURE, error_message=error_message)


# Import fix for datetime
from datetime import timedelta
