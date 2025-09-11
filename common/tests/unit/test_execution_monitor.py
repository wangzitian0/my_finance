#!/usr/bin/env python3
"""
Unit tests for execution_monitor.py - Agent Execution Monitoring System
Tests execution tracking, error categorization, and performance metrics.
"""

import json
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from common.monitoring.execution_monitor import (
    ErrorCategory,
    ExecutionLog,
    ExecutionMonitor,
    ExecutionResult,
    get_monitor,
    log_failure,
    log_success,
    monitor_execution,
)


@pytest.mark.monitoring
class TestErrorCategory:
    """Test ErrorCategory enum."""

    def test_error_category_values(self):
        """Test error category enum values."""
        assert ErrorCategory.CRITICAL.value == "critical"
        assert ErrorCategory.HIGH.value == "high"
        assert ErrorCategory.MEDIUM.value == "medium"
        assert ErrorCategory.LOW.value == "low"


@pytest.mark.monitoring
class TestExecutionResult:
    """Test ExecutionResult enum."""

    def test_execution_result_values(self):
        """Test execution result enum values."""
        assert ExecutionResult.SUCCESS.value == "success"
        assert ExecutionResult.FAILURE.value == "failure"
        assert ExecutionResult.TIMEOUT.value == "timeout"
        assert ExecutionResult.RETRY.value == "retry"


@pytest.mark.monitoring
class TestExecutionLog:
    """Test ExecutionLog dataclass."""

    def test_execution_log_creation(self):
        """Test ExecutionLog creation."""
        log = ExecutionLog(
            timestamp="2025-01-01T10:00:00",
            agent_type="test-agent",
            task_description="Test task",
            execution_result="success",
            error_category=None,
            execution_time_ms=1000,
            retry_count=0,
            environment_state={"test": True},
            error_message=None,
            stack_trace=None,
            command="test command",
            working_directory="/test",
        )

        assert log.agent_type == "test-agent"
        assert log.execution_result == "success"
        assert log.execution_time_ms == 1000
        assert log.environment_state == {"test": True}


@pytest.mark.monitoring
class TestExecutionMonitor:
    """Test ExecutionMonitor core functionality."""

    def test_initialization_with_custom_directory(self):
        """Test monitor initialization with custom log directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "custom_logs"
            monitor = ExecutionMonitor(log_directory=log_dir)

            assert monitor.log_directory == log_dir
            assert log_dir.exists()

    def test_initialization_with_default_directory(self):
        """Test monitor initialization with default directory."""
        with patch("common.monitoring.execution_monitor.directory_manager") as mock_dm:
            with tempfile.TemporaryDirectory() as temp_dir:
                mock_dm.get_logs_path.return_value = Path(temp_dir) / "logs"
                monitor = ExecutionMonitor()

                assert monitor.log_directory.exists()
                mock_dm.get_logs_path.assert_called_once()

    def test_start_execution(self):
        """Test execution start tracking."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = ExecutionMonitor(log_directory=Path(temp_dir))

            agent_type = "test-agent"
            task_description = "Test task"
            command = "test command"

            monitor.start_execution(agent_type, task_description, command)

            assert monitor._agent_type == agent_type
            assert monitor._task_description == task_description
            assert monitor._command == command
            assert monitor._start_time is not None
            assert monitor._retry_count == 0

    def test_increment_retry(self):
        """Test retry counter increment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = ExecutionMonitor(log_directory=Path(temp_dir))
            monitor.start_execution("test-agent", "Test task")

            initial_count = monitor._retry_count
            monitor.increment_retry()

            assert monitor._retry_count == initial_count + 1

            monitor.increment_retry()
            assert monitor._retry_count == initial_count + 2


@pytest.mark.monitoring
class TestErrorCategorization:
    """Test error categorization logic."""

    @pytest.fixture
    def monitor(self):
        """Create monitor for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield ExecutionMonitor(log_directory=Path(temp_dir))

    def test_categorize_critical_errors(self, monitor):
        """Test critical error categorization."""
        critical_errors = [
            "Segmentation fault occurred",
            "Memory error detected",
            "System error in process",
            "Database corrupted",
            "Database connection lost",
            "Disk full error",
            "Permission denied",
            "Authentication failed",
        ]

        for error_msg in critical_errors:
            category = monitor._categorize_error(error_msg)
            assert category == ErrorCategory.CRITICAL

    def test_categorize_high_errors(self, monitor):
        """Test high priority error categorization."""
        high_errors = [
            "ImportError: module not found",
            "ModuleNotFoundError",
            "FileNotFoundError",
            "Network error occurred",
            "Request timeout",
            "Connection refused",
            "Invalid configuration",
        ]

        for error_msg in high_errors:
            category = monitor._categorize_error(error_msg)
            assert category == ErrorCategory.HIGH

    def test_categorize_medium_errors(self, monitor):
        """Test medium priority error categorization."""
        medium_errors = [
            "Warning: deprecated function",
            "Invalid input provided",
            "Parsing error in file",
            "Format error detected",
        ]

        for error_msg in medium_errors:
            category = monitor._categorize_error(error_msg)
            assert category == ErrorCategory.MEDIUM

    def test_categorize_low_errors(self, monitor):
        """Test low priority error categorization."""
        low_errors = ["Unknown error", "Custom error message", "", None]

        for error_msg in low_errors:
            category = monitor._categorize_error(error_msg)
            assert category == ErrorCategory.LOW

    def test_categorize_case_insensitive(self, monitor):
        """Test error categorization is case insensitive."""
        errors = ["SEGMENTATION FAULT", "Import Error", "WARNING MESSAGE", "unknown error"]

        expected_categories = [
            ErrorCategory.CRITICAL,
            ErrorCategory.HIGH,
            ErrorCategory.MEDIUM,
            ErrorCategory.LOW,
        ]

        for error_msg, expected in zip(errors, expected_categories):
            category = monitor._categorize_error(error_msg)
            assert category == expected


@pytest.mark.monitoring
class TestEnvironmentCapture:
    """Test environment state capture."""

    def test_get_environment_state(self):
        """Test environment state capture."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = ExecutionMonitor(log_directory=Path(temp_dir))

            with patch(
                "common.monitoring.execution_monitor.Path.cwd", return_value=Path("/test/dir")
            ):
                env_state = monitor._get_environment_state()

                assert "working_directory" in env_state
                assert "python_version" in env_state
                assert "environment_variables" in env_state
                assert "timestamp" in env_state
                assert "process_id" in env_state

                assert env_state["working_directory"] == "/test/dir"
                assert isinstance(env_state["environment_variables"], dict)
                assert isinstance(env_state["process_id"], int)


@pytest.mark.monitoring
class TestExecutionLogging:
    """Test execution logging functionality."""

    @pytest.fixture
    def monitor(self):
        """Create monitor for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield ExecutionMonitor(log_directory=Path(temp_dir))

    def test_log_successful_execution(self, monitor):
        """Test logging successful execution."""
        monitor.start_execution("test-agent", "Test task", "test command")
        time.sleep(0.01)  # Small delay for execution time

        log_entry = monitor.log_execution(ExecutionResult.SUCCESS)

        assert log_entry is not None
        assert log_entry.agent_type == "test-agent"
        assert log_entry.task_description == "Test task"
        assert log_entry.command == "test command"
        assert log_entry.execution_result == "success"
        assert log_entry.error_category is None
        assert log_entry.execution_time_ms > 0
        assert log_entry.retry_count == 0

    def test_log_failed_execution(self, monitor):
        """Test logging failed execution."""
        monitor.start_execution("test-agent", "Test task")
        error_message = "Test error message"
        stack_trace = "Test stack trace"

        log_entry = monitor.log_execution(
            ExecutionResult.FAILURE, error_message=error_message, stack_trace=stack_trace
        )

        assert log_entry is not None
        assert log_entry.execution_result == "failure"
        assert log_entry.error_message == error_message
        assert log_entry.stack_trace == stack_trace
        assert log_entry.error_category == "low"  # Default categorization

    def test_log_execution_with_retries(self, monitor):
        """Test logging execution with retries."""
        monitor.start_execution("test-agent", "Test task")
        monitor.increment_retry()
        monitor.increment_retry()

        log_entry = monitor.log_execution(ExecutionResult.SUCCESS)

        assert log_entry.retry_count == 2

    def test_log_execution_without_start(self, monitor):
        """Test logging execution without calling start_execution."""
        log_entry = monitor.log_execution(ExecutionResult.SUCCESS)

        assert log_entry is None

    def test_log_entry_saves_to_file(self, monitor):
        """Test log entry is saved to daily file."""
        monitor.start_execution("test-agent", "Test task")

        log_entry = monitor.log_execution(ExecutionResult.SUCCESS)

        # Check log file was created
        log_date = datetime.now().strftime("%Y-%m-%d")
        log_file = monitor.log_directory / f"execution_logs_{log_date}.json"

        assert log_file.exists()

        # Check log entry was saved
        with open(log_file, "r") as f:
            logs = json.load(f)

        assert len(logs) == 1
        assert logs[0]["agent_type"] == "test-agent"
        assert logs[0]["execution_result"] == "success"


@pytest.mark.monitoring
class TestExecutionStatistics:
    """Test execution statistics generation."""

    @pytest.fixture
    def populated_monitor(self):
        """Create monitor with sample execution logs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = ExecutionMonitor(log_directory=Path(temp_dir))

            # Create sample log entries for multiple days
            agents = ["agent-1", "agent-2", "agent-3"]
            results = [ExecutionResult.SUCCESS, ExecutionResult.FAILURE]

            for days_ago in range(3):
                date = datetime.now() - timedelta(days=days_ago)
                log_date = date.strftime("%Y-%m-%d")
                log_file = monitor.log_directory / f"execution_logs_{log_date}.json"

                daily_logs = []
                for i in range(5):  # 5 logs per day
                    log_entry = {
                        "timestamp": date.isoformat(),
                        "agent_type": agents[i % len(agents)],
                        "task_description": f"Task {i}",
                        "execution_result": results[i % len(results)].value,
                        "error_category": (
                            "medium"
                            if results[i % len(results)] == ExecutionResult.FAILURE
                            else None
                        ),
                        "execution_time_ms": (i + 1) * 100,
                        "retry_count": i % 3,
                        "environment_state": {},
                        "error_message": (
                            f"Error {i}"
                            if results[i % len(results)] == ExecutionResult.FAILURE
                            else None
                        ),
                        "stack_trace": None,
                        "command": None,
                        "working_directory": "/test",
                    }
                    daily_logs.append(log_entry)

                with open(log_file, "w") as f:
                    json.dump(daily_logs, f)

            yield monitor

    def test_get_execution_stats_basic(self, populated_monitor):
        """Test basic execution statistics."""
        stats = populated_monitor.get_execution_stats(days=7)

        assert stats["total_executions"] == 15  # 3 days * 5 logs
        assert stats["success_count"] > 0
        assert stats["failure_count"] > 0
        assert stats["average_execution_time_ms"] > 0
        assert "success_rate" in stats

        # Verify success rate calculation
        expected_rate = stats["success_count"] / stats["total_executions"]
        assert abs(stats["success_rate"] - expected_rate) < 0.001

    def test_get_execution_stats_error_categories(self, populated_monitor):
        """Test error category statistics."""
        stats = populated_monitor.get_execution_stats(days=7)

        assert "error_categories" in stats
        if stats["failure_count"] > 0:
            assert "medium" in stats["error_categories"]
            assert stats["error_categories"]["medium"] > 0

    def test_get_execution_stats_agent_performance(self, populated_monitor):
        """Test agent performance statistics."""
        stats = populated_monitor.get_execution_stats(days=7)

        assert "agent_performance" in stats

        for agent_type, performance in stats["agent_performance"].items():
            assert "total" in performance
            assert "success" in performance
            assert "failure" in performance
            assert performance["total"] == performance["success"] + performance["failure"]

    def test_get_execution_stats_retry_patterns(self, populated_monitor):
        """Test retry pattern statistics."""
        stats = populated_monitor.get_execution_stats(days=7)

        assert "retry_patterns" in stats
        # Should have retry patterns since we created logs with different retry counts
        if any(log["retry_count"] > 0 for log in self._get_all_logs(populated_monitor)):
            assert len(stats["retry_patterns"]) > 0

    def test_get_execution_stats_no_logs(self):
        """Test statistics with no log files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = ExecutionMonitor(log_directory=Path(temp_dir))
            stats = monitor.get_execution_stats(days=7)

            assert stats["total_executions"] == 0
            assert stats["success_count"] == 0
            assert stats["failure_count"] == 0
            assert stats["average_execution_time_ms"] == 0
            assert len(stats["error_categories"]) == 0
            assert len(stats["agent_performance"]) == 0
            assert len(stats["retry_patterns"]) == 0

    def test_get_execution_stats_corrupted_logs(self, populated_monitor):
        """Test statistics with corrupted log files."""
        # Create corrupted log file
        corrupted_file = populated_monitor.log_directory / "execution_logs_2025-01-04.json"
        corrupted_file.write_text("invalid json content")

        # Should handle gracefully
        stats = populated_monitor.get_execution_stats(days=7)
        assert stats["total_executions"] >= 0  # Should not crash

    def _get_all_logs(self, monitor):
        """Helper to get all logs from monitor."""
        all_logs = []
        for log_file in monitor.log_directory.glob("execution_logs_*.json"):
            try:
                with open(log_file, "r") as f:
                    logs = json.load(f)
                    all_logs.extend(logs)
            except json.JSONDecodeError:
                continue
        return all_logs


@pytest.mark.monitoring
class TestGlobalMonitor:
    """Test global monitor functionality."""

    def test_get_monitor_singleton(self):
        """Test global monitor is singleton."""
        monitor1 = get_monitor()
        monitor2 = get_monitor()

        assert monitor1 is monitor2

    def test_get_monitor_creates_instance(self):
        """Test get_monitor creates ExecutionMonitor instance."""
        # Clear global monitor
        import common.monitoring.execution_monitor

        common.monitoring.execution_monitor._global_monitor = None

        monitor = get_monitor()
        assert isinstance(monitor, ExecutionMonitor)


@pytest.mark.monitoring
class TestMonitorDecorator:
    """Test monitor_execution decorator."""

    def test_monitor_execution_success(self):
        """Test decorator with successful execution."""

        @monitor_execution("test-agent", "Test task", "test command")
        def test_function():
            return "success"

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("common.monitoring.execution_monitor.get_monitor") as mock_get:
                mock_monitor = MagicMock()
                mock_get.return_value = mock_monitor

                result = test_function()

                assert result == "success"
                mock_monitor.start_execution.assert_called_once_with(
                    "test-agent", "Test task", "test command"
                )
                mock_monitor.log_execution.assert_called_once_with(ExecutionResult.SUCCESS)

    def test_monitor_execution_failure(self):
        """Test decorator with failed execution."""

        @monitor_execution("test-agent", "Test task")
        def test_function():
            raise ValueError("Test error")

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("common.monitoring.execution_monitor.get_monitor") as mock_get:
                mock_monitor = MagicMock()
                mock_get.return_value = mock_monitor

                with pytest.raises(ValueError):
                    test_function()

                mock_monitor.start_execution.assert_called_once_with(
                    "test-agent", "Test task", None
                )
                mock_monitor.log_execution.assert_called_once()

                # Check error was logged
                call_args = mock_monitor.log_execution.call_args[0]
                assert call_args[0] == ExecutionResult.FAILURE

                call_kwargs = mock_monitor.log_execution.call_args[1]
                assert "Test error" in call_kwargs["error_message"]
                assert "stack_trace" in call_kwargs


@pytest.mark.monitoring
class TestConvenienceFunctions:
    """Test convenience logging functions."""

    def test_log_success(self):
        """Test log_success convenience function."""
        with patch("common.monitoring.execution_monitor.get_monitor") as mock_get:
            mock_monitor = MagicMock()
            mock_get.return_value = mock_monitor

            log_success("test-agent", "Test task", execution_time_ms=1000)

            mock_monitor.start_execution.assert_called_once_with("test-agent", "Test task")
            mock_monitor.log_execution.assert_called_once_with(ExecutionResult.SUCCESS)

    def test_log_failure(self):
        """Test log_failure convenience function."""
        with patch("common.monitoring.execution_monitor.get_monitor") as mock_get:
            mock_monitor = MagicMock()
            mock_get.return_value = mock_monitor

            log_failure("test-agent", "Test task", "Test error", execution_time_ms=2000)

            mock_monitor.start_execution.assert_called_once_with("test-agent", "Test task")
            mock_monitor.log_execution.assert_called_once_with(
                ExecutionResult.FAILURE, error_message="Test error"
            )


@pytest.mark.integration
class TestExecutionMonitorIntegration:
    """Integration tests for ExecutionMonitor."""

    def test_complete_monitoring_workflow(self):
        """Test complete monitoring workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = ExecutionMonitor(log_directory=Path(temp_dir))

            # Successful execution
            monitor.start_execution("workflow-agent", "Test workflow", "test command")
            time.sleep(0.01)
            success_log = monitor.log_execution(ExecutionResult.SUCCESS)

            assert success_log is not None
            assert success_log.execution_result == "success"
            assert success_log.execution_time_ms > 0

            # Failed execution with retries
            monitor.start_execution("workflow-agent", "Failed workflow")
            monitor.increment_retry()
            monitor.increment_retry()
            failure_log = monitor.log_execution(
                ExecutionResult.FAILURE,
                error_message="Import error occurred",
                stack_trace="Traceback...",
            )

            assert failure_log.execution_result == "failure"
            assert failure_log.retry_count == 2
            assert failure_log.error_category == "high"  # Import error

            # Get statistics
            stats = monitor.get_execution_stats(days=1)

            assert stats["total_executions"] == 2
            assert stats["success_count"] == 1
            assert stats["failure_count"] == 1
            assert stats["success_rate"] == 0.5

            # Check agent performance
            agent_perf = stats["agent_performance"]["workflow-agent"]
            assert agent_perf["total"] == 2
            assert agent_perf["success"] == 1
            assert agent_perf["failure"] == 1

            # Check error categories
            assert "high" in stats["error_categories"]
            assert stats["error_categories"]["high"] == 1

            # Check retry patterns
            assert 2 in stats["retry_patterns"]
            assert stats["retry_patterns"][2] == 1
