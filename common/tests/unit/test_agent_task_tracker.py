#!/usr/bin/env python3
"""
Unit tests for agent_task_tracker.py - Agent Task Outcome Tracking
Tests database operations, performance analysis, and error tracking.
"""

import json
import sqlite3
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from common.agents.agent_task_tracker import AgentTask, AgentTaskTracker, get_tracker
from common.monitoring.execution_monitor import ErrorCategory, ExecutionLog, ExecutionResult


@pytest.mark.agents
class TestAgentTask:
    """Test AgentTask dataclass."""

    def test_agent_task_creation(self):
        """Test AgentTask dataclass creation."""
        start_time = datetime.now()
        task = AgentTask(
            task_id="test-123",
            agent_type="test-agent",
            task_description="Test task",
            start_time=start_time,
            end_time=None,
            execution_result="pending",
            error_category=None,
            execution_time_ms=0,
            retry_count=0,
            error_message=None,
            stack_trace=None,
            command=None,
            working_directory="/test",
            environment_state={},
        )

        assert task.task_id == "test-123"
        assert task.agent_type == "test-agent"
        assert task.start_time == start_time
        assert task.execution_result == "pending"


@pytest.mark.agents
class TestAgentTaskTracker:
    """Test AgentTaskTracker database operations."""

    def test_initialization_with_custom_path(self):
        """Test tracker initialization with custom database path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "custom_tasks.db"
            tracker = AgentTaskTracker(db_path)

            assert tracker.db_path == db_path
            assert db_path.exists()

    def test_initialization_with_default_path(self):
        """Test tracker initialization with default path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("common.agents.agent_task_tracker.Path.cwd", return_value=Path(temp_dir)):
                tracker = AgentTaskTracker()

                # Check that database was created
                assert tracker.db_path.exists()
                assert "agent_tasks.db" in str(tracker.db_path)

    def test_database_schema_creation(self):
        """Test database schema is created correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            tracker = AgentTaskTracker(db_path)

            # Check tables and indexes exist
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor]
                assert "agent_tasks" in tables

                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
                indexes = [row[0] for row in cursor]
                index_names = [
                    "idx_agent_type",
                    "idx_start_time",
                    "idx_execution_result",
                    "idx_error_category",
                ]
                for idx_name in index_names:
                    assert idx_name in indexes

    def test_create_task(self):
        """Test task creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            tracker = AgentTaskTracker(db_path)

            task_id = tracker.create_task(
                agent_type="test-agent", task_description="Test task", command="test command"
            )

            assert task_id is not None
            assert len(task_id) == 36  # UUID4 length

            # Verify task in database
            task = tracker.get_task(task_id)
            assert task is not None
            assert task.agent_type == "test-agent"
            assert task.task_description == "Test task"
            assert task.command == "test command"

    def test_create_subtask(self):
        """Test subtask creation with parent relationship."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            tracker = AgentTaskTracker(db_path)

            # Create parent task
            parent_id = tracker.create_task(
                agent_type="parent-agent", task_description="Parent task"
            )

            # Create subtask
            child_id = tracker.create_task(
                agent_type="child-agent", task_description="Child task", parent_task_id=parent_id
            )

            # Verify parent-child relationship
            parent_task = tracker.get_task(parent_id)
            child_task = tracker.get_task(child_id)

            assert parent_task.subtask_count == 1
            assert child_task.parent_task_id == parent_id

    def test_complete_task_success(self):
        """Test successful task completion."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            tracker = AgentTaskTracker(db_path)

            task_id = tracker.create_task(agent_type="test-agent", task_description="Test task")

            # Add small delay to ensure measurable execution time
            time.sleep(0.001)

            # Complete task successfully
            environment_state = {"key": "value"}
            tracker.complete_task(
                task_id=task_id,
                execution_result=ExecutionResult.SUCCESS,
                environment_state=environment_state,
            )

            # Verify completion
            task = tracker.get_task(task_id)
            assert task.execution_result == "success"
            assert task.end_time is not None
            assert task.execution_time_ms > 0
            assert task.environment_state == environment_state

    def test_complete_task_failure(self):
        """Test failed task completion."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            tracker = AgentTaskTracker(db_path)

            task_id = tracker.create_task(agent_type="test-agent", task_description="Test task")

            # Complete task with failure
            tracker.complete_task(
                task_id=task_id,
                execution_result=ExecutionResult.FAILURE,
                error_message="Test error",
                error_category=ErrorCategory.MEDIUM,
                retry_count=2,
                stack_trace="Test stack trace",
            )

            # Verify failure details
            task = tracker.get_task(task_id)
            assert task.execution_result == "failure"
            assert task.error_message == "Test error"
            assert task.error_category == "medium"
            assert task.retry_count == 2
            assert task.stack_trace == "Test stack trace"

    def test_complete_nonexistent_task(self):
        """Test completing non-existent task raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            tracker = AgentTaskTracker(db_path)

            with pytest.raises(ValueError, match="Task .* not found"):
                tracker.complete_task(
                    task_id="nonexistent", execution_result=ExecutionResult.SUCCESS
                )

    def test_get_nonexistent_task(self):
        """Test getting non-existent task returns None."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            tracker = AgentTaskTracker(db_path)

            task = tracker.get_task("nonexistent")
            assert task is None

    def test_row_to_agent_task_with_invalid_json(self):
        """Test handling invalid JSON in environment_state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            tracker = AgentTaskTracker(db_path)

            # Insert task with invalid JSON
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO agent_tasks (
                        task_id, agent_type, task_description, start_time,
                        execution_result, execution_time_ms, retry_count,
                        working_directory, environment_state
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "test-invalid-json",
                        "test-agent",
                        "Test task",
                        datetime.now(),
                        "success",
                        100,
                        0,
                        "/test",
                        "invalid json",  # Invalid JSON
                    ),
                )
                conn.commit()

            # Should handle gracefully
            task = tracker.get_task("test-invalid-json")
            assert task is not None
            assert task.environment_state == {}  # Should default to empty dict


@pytest.mark.agents
class TestAgentPerformanceAnalysis:
    """Test agent performance analysis methods."""

    @pytest.fixture
    def populated_tracker(self):
        """Create tracker with sample data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            tracker = AgentTaskTracker(db_path)

            # Create sample tasks for different agents
            agents = ["agent-1", "agent-2", "agent-3"]
            results = [ExecutionResult.SUCCESS, ExecutionResult.FAILURE]
            categories = [
                ErrorCategory.LOW,
                ErrorCategory.MEDIUM,
                ErrorCategory.HIGH,
                ErrorCategory.CRITICAL,
            ]

            for i in range(20):
                task_id = tracker.create_task(
                    agent_type=agents[i % len(agents)], task_description=f"Task {i}"
                )

                result = results[i % len(results)]
                error_category = (
                    categories[i % len(categories)] if result == ExecutionResult.FAILURE else None
                )
                error_message = f"Error {i}" if result == ExecutionResult.FAILURE else None

                tracker.complete_task(
                    task_id=task_id,
                    execution_result=result,
                    error_message=error_message,
                    error_category=error_category,
                    retry_count=i % 3,
                )

            yield tracker

    def test_get_agent_performance(self, populated_tracker):
        """Test agent performance statistics."""
        performance = populated_tracker.get_agent_performance(days=7)

        assert len(performance) == 3  # 3 different agents

        for agent_type, metrics in performance.items():
            assert "total_tasks" in metrics
            assert "success_count" in metrics
            assert "failure_count" in metrics
            assert "success_rate" in metrics
            assert "avg_execution_time_ms" in metrics
            assert "total_retries" in metrics
            assert "error_breakdown" in metrics

            # Check error breakdown structure
            error_breakdown = metrics["error_breakdown"]
            assert "critical" in error_breakdown
            assert "high" in error_breakdown
            assert "medium" in error_breakdown
            assert "low" in error_breakdown

            # Verify success rate calculation
            total = metrics["total_tasks"]
            success = metrics["success_count"]
            expected_rate = success / total if total > 0 else 0
            assert abs(metrics["success_rate"] - expected_rate) < 0.001

    def test_get_error_patterns(self, populated_tracker):
        """Test error pattern analysis."""
        patterns = populated_tracker.get_error_patterns(days=7)

        assert len(patterns) > 0

        for pattern in patterns:
            assert "error_message" in pattern
            assert "error_category" in pattern
            assert "agent_type" in pattern
            assert "frequency" in pattern
            assert "avg_retries" in pattern
            assert "first_occurrence" in pattern
            assert "last_occurrence" in pattern

            assert pattern["frequency"] > 0
            assert pattern["avg_retries"] >= 0

    def test_get_performance_trends(self, populated_tracker):
        """Test performance trends analysis."""
        trends = populated_tracker.get_performance_trends(days=30)

        assert len(trends) == 3  # 3 different agents

        for agent_type, trend_data in trends.items():
            assert len(trend_data) > 0

            for day_data in trend_data:
                assert "date" in day_data
                assert "total_tasks" in day_data
                assert "success_count" in day_data
                assert "success_rate" in day_data
                assert "avg_execution_time_ms" in day_data

                # Verify success rate calculation
                total = day_data["total_tasks"]
                success = day_data["success_count"]
                expected_rate = success / total if total > 0 else 0
                assert abs(day_data["success_rate"] - expected_rate) < 0.001

    def test_import_execution_log(self):
        """Test importing ExecutionLog into task database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            tracker = AgentTaskTracker(db_path)

            # Create ExecutionLog
            execution_log = ExecutionLog(
                timestamp="2025-01-01T10:00:00Z",
                agent_type="test-agent",
                task_description="Imported task",
                execution_result="success",
                error_category=None,
                execution_time_ms=500,
                retry_count=1,
                error_message=None,
                stack_trace=None,
                command="test command",
                working_directory="/test",
                environment_state={"imported": True},
            )

            task_id = tracker.import_execution_log(execution_log)

            # Verify import
            task = tracker.get_task(task_id)
            assert task is not None
            assert task.agent_type == "test-agent"
            assert task.task_description == "Imported task"
            assert task.execution_result == "success"
            assert task.execution_time_ms == 500
            assert task.retry_count == 1
            assert task.command == "test command"
            assert task.environment_state == {"imported": True}


@pytest.mark.agents
class TestGlobalTracker:
    """Test global tracker singleton."""

    def test_get_tracker_singleton(self):
        """Test global tracker is singleton."""
        tracker1 = get_tracker()
        tracker2 = get_tracker()

        assert tracker1 is tracker2

    def test_get_tracker_creates_instance(self):
        """Test get_tracker creates AgentTaskTracker instance."""
        # Clear global tracker
        import common.agents.agent_task_tracker

        common.agents.agent_task_tracker._global_tracker = None

        tracker = get_tracker()
        assert isinstance(tracker, AgentTaskTracker)
        assert tracker.db_path.exists()


@pytest.mark.integration
class TestAgentTaskTrackerIntegration:
    """Integration tests for AgentTaskTracker."""

    def test_complete_workflow(self):
        """Test complete task tracking workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "workflow_test.db"
            tracker = AgentTaskTracker(db_path)

            # Create and complete multiple tasks
            task_ids = []

            # Successful task
            task_id = tracker.create_task(
                agent_type="workflow-agent", task_description="Successful task"
            )
            task_ids.append(task_id)

            # Add small delay to ensure measurable execution time
            time.sleep(0.001)

            tracker.complete_task(
                task_id=task_id,
                execution_result=ExecutionResult.SUCCESS,
                environment_state={"workflow": "success"},
            )

            # Failed task
            task_id = tracker.create_task(
                agent_type="workflow-agent", task_description="Failed task"
            )
            task_ids.append(task_id)

            # Add small delay to ensure measurable execution time
            time.sleep(0.001)

            tracker.complete_task(
                task_id=task_id,
                execution_result=ExecutionResult.FAILURE,
                error_message="Workflow failure",
                error_category=ErrorCategory.HIGH,
                retry_count=2,
            )

            # Verify all tasks
            for task_id in task_ids:
                task = tracker.get_task(task_id)
                assert task is not None
                assert task.end_time is not None
                assert task.execution_time_ms > 0

            # Verify performance analysis
            performance = tracker.get_agent_performance()
            assert "workflow-agent" in performance

            agent_perf = performance["workflow-agent"]
            assert agent_perf["total_tasks"] == 2
            assert agent_perf["success_count"] == 1
            assert agent_perf["failure_count"] == 1
            assert agent_perf["success_rate"] == 0.5
