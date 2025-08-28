#!/usr/bin/env python3
"""
Agent Task Outcome Tracking Database Structure

Provides comprehensive tracking for agent task outcomes and performance
analysis as part of the Agent Execution Monitoring System (Issue #180).
"""
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .execution_monitor import ErrorCategory, ExecutionLog, ExecutionResult


@dataclass
class AgentTask:
    """Agent task record structure."""

    task_id: str
    agent_type: str
    task_description: str
    start_time: datetime
    end_time: Optional[datetime]
    execution_result: str
    error_category: Optional[str]
    execution_time_ms: int
    retry_count: int
    error_message: Optional[str]
    stack_trace: Optional[str]
    command: Optional[str]
    working_directory: str
    environment_state: Dict[str, Any]
    parent_task_id: Optional[str] = None
    subtask_count: int = 0


class AgentTaskTracker:
    """
    Database for tracking agent task outcomes.

    Provides structured storage and querying capabilities for agent
    performance analysis and HRBP review mechanisms.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize agent task tracker."""
        if db_path is None:
            # Use common/config/monitoring/ directory
            config_dir = Path(__file__).parent / "config" / "monitoring"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = config_dir / "agent_tasks.db"
        else:
            self.db_path = Path(db_path)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_tasks (
                    task_id TEXT PRIMARY KEY,
                    agent_type TEXT NOT NULL,
                    task_description TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    execution_result TEXT NOT NULL,
                    error_category TEXT,
                    execution_time_ms INTEGER DEFAULT 0,
                    retry_count INTEGER DEFAULT 0,
                    error_message TEXT,
                    stack_trace TEXT,
                    command TEXT,
                    working_directory TEXT,
                    environment_state TEXT,  -- JSON serialized
                    parent_task_id TEXT,
                    subtask_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_task_id) REFERENCES agent_tasks(task_id)
                )
            """
            )

            # Create indexes for performance
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_type 
                ON agent_tasks(agent_type)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_start_time 
                ON agent_tasks(start_time)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_execution_result 
                ON agent_tasks(execution_result)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_error_category 
                ON agent_tasks(error_category)
            """
            )

            conn.commit()

    def create_task(
        self,
        agent_type: str,
        task_description: str,
        command: Optional[str] = None,
        parent_task_id: Optional[str] = None,
    ) -> str:
        """
        Create a new task record.

        Args:
            agent_type: Type of agent executing the task
            task_description: Human-readable task description
            command: Command being executed (if applicable)
            parent_task_id: Parent task ID for subtasks

        Returns:
            str: Task ID for tracking
        """
        task_id = str(uuid.uuid4())
        start_time = datetime.now()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO agent_tasks (
                    task_id, agent_type, task_description, start_time,
                    command, working_directory, parent_task_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task_id,
                    agent_type,
                    task_description,
                    start_time,
                    command,
                    str(Path.cwd()),
                    parent_task_id,
                ),
            )

            # Update parent task subtask count
            if parent_task_id:
                conn.execute(
                    """
                    UPDATE agent_tasks 
                    SET subtask_count = subtask_count + 1
                    WHERE task_id = ?
                """,
                    (parent_task_id,),
                )

            conn.commit()

        return task_id

    def complete_task(
        self,
        task_id: str,
        execution_result: ExecutionResult,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        error_category: Optional[ErrorCategory] = None,
        retry_count: int = 0,
        environment_state: Optional[Dict[str, Any]] = None,
    ):
        """
        Mark a task as completed with outcome.

        Args:
            task_id: Task ID to update
            execution_result: Final execution result
            error_message: Error message if failed
            stack_trace: Stack trace if available
            error_category: Categorized error level
            retry_count: Number of retries attempted
            environment_state: Environment state snapshot
        """
        end_time = datetime.now()

        # Calculate execution time from start time
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT start_time FROM agent_tasks WHERE task_id = ?
            """,
                (task_id,),
            )

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Task {task_id} not found")

            start_time = datetime.fromisoformat(row[0])
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

            # Update task record
            conn.execute(
                """
                UPDATE agent_tasks SET
                    end_time = ?,
                    execution_result = ?,
                    execution_time_ms = ?,
                    retry_count = ?,
                    error_message = ?,
                    stack_trace = ?,
                    error_category = ?,
                    environment_state = ?
                WHERE task_id = ?
            """,
                (
                    end_time,
                    execution_result.value,
                    execution_time_ms,
                    retry_count,
                    error_message,
                    stack_trace,
                    error_category.value if error_category else None,
                    json.dumps(environment_state) if environment_state else None,
                    task_id,
                ),
            )

            conn.commit()

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get task by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM agent_tasks WHERE task_id = ?
            """,
                (task_id,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            return self._row_to_agent_task(row)

    def _row_to_agent_task(self, row: sqlite3.Row) -> AgentTask:
        """Convert database row to AgentTask."""
        environment_state = {}
        if row["environment_state"]:
            try:
                environment_state = json.loads(row["environment_state"])
            except json.JSONDecodeError:
                environment_state = {}

        return AgentTask(
            task_id=row["task_id"],
            agent_type=row["agent_type"],
            task_description=row["task_description"],
            start_time=datetime.fromisoformat(row["start_time"]),
            end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
            execution_result=row["execution_result"],
            error_category=row["error_category"],
            execution_time_ms=row["execution_time_ms"],
            retry_count=row["retry_count"],
            error_message=row["error_message"],
            stack_trace=row["stack_trace"],
            command=row["command"],
            working_directory=row["working_directory"],
            environment_state=environment_state,
            parent_task_id=row["parent_task_id"],
            subtask_count=row["subtask_count"],
        )

    def get_agent_performance(self, days: int = 7) -> Dict[str, Any]:
        """
        Get agent performance statistics.

        Args:
            days: Number of days to analyze

        Returns:
            Dict with performance metrics by agent type
        """
        since_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    agent_type,
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN execution_result = 'success' THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN execution_result = 'failure' THEN 1 ELSE 0 END) as failure_count,
                    AVG(execution_time_ms) as avg_execution_time,
                    SUM(retry_count) as total_retries,
                    COUNT(CASE WHEN error_category = 'critical' THEN 1 END) as critical_errors,
                    COUNT(CASE WHEN error_category = 'high' THEN 1 END) as high_errors,
                    COUNT(CASE WHEN error_category = 'medium' THEN 1 END) as medium_errors,
                    COUNT(CASE WHEN error_category = 'low' THEN 1 END) as low_errors
                FROM agent_tasks 
                WHERE start_time >= ?
                GROUP BY agent_type
                ORDER BY total_tasks DESC
            """,
                (since_date,),
            )

            results = {}
            for row in cursor:
                agent_type = row[0]
                total_tasks = row[1]
                success_count = row[2]
                failure_count = row[3]

                results[agent_type] = {
                    "total_tasks": total_tasks,
                    "success_count": success_count,
                    "failure_count": failure_count,
                    "success_rate": success_count / total_tasks if total_tasks > 0 else 0,
                    "avg_execution_time_ms": row[4] or 0,
                    "total_retries": row[5],
                    "error_breakdown": {
                        "critical": row[6],
                        "high": row[7],
                        "medium": row[8],
                        "low": row[9],
                    },
                }

            return results

    def get_error_patterns(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get error patterns for analysis.

        Args:
            days: Number of days to analyze

        Returns:
            List of error patterns with frequencies
        """
        since_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    error_message,
                    error_category,
                    agent_type,
                    COUNT(*) as frequency,
                    AVG(retry_count) as avg_retries,
                    MIN(start_time) as first_occurrence,
                    MAX(start_time) as last_occurrence
                FROM agent_tasks 
                WHERE start_time >= ? 
                  AND execution_result = 'failure'
                  AND error_message IS NOT NULL
                GROUP BY error_message, error_category, agent_type
                ORDER BY frequency DESC
            """,
                (since_date,),
            )

            patterns = []
            for row in cursor:
                patterns.append(
                    {
                        "error_message": row[0],
                        "error_category": row[1],
                        "agent_type": row[2],
                        "frequency": row[3],
                        "avg_retries": row[4],
                        "first_occurrence": row[5],
                        "last_occurrence": row[6],
                    }
                )

            return patterns

    def get_performance_trends(self, days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get performance trends over time.

        Args:
            days: Number of days to analyze

        Returns:
            Dict with daily performance trends by agent type
        """
        since_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    agent_type,
                    DATE(start_time) as task_date,
                    COUNT(*) as total_tasks,
                    SUM(CASE WHEN execution_result = 'success' THEN 1 ELSE 0 END) as success_count,
                    AVG(execution_time_ms) as avg_execution_time
                FROM agent_tasks 
                WHERE start_time >= ?
                GROUP BY agent_type, DATE(start_time)
                ORDER BY agent_type, task_date
            """,
                (since_date,),
            )

            trends = {}
            for row in cursor:
                agent_type = row[0]
                if agent_type not in trends:
                    trends[agent_type] = []

                total_tasks = row[2]
                success_count = row[3]

                trends[agent_type].append(
                    {
                        "date": row[1],
                        "total_tasks": total_tasks,
                        "success_count": success_count,
                        "success_rate": success_count / total_tasks if total_tasks > 0 else 0,
                        "avg_execution_time_ms": row[4] or 0,
                    }
                )

            return trends

    def import_execution_log(self, execution_log: ExecutionLog) -> str:
        """
        Import an execution log entry into the task database.

        Args:
            execution_log: ExecutionLog to import

        Returns:
            str: Generated task ID
        """
        task_id = str(uuid.uuid4())

        # Parse timestamp
        start_time = datetime.fromisoformat(execution_log.timestamp.replace("Z", "+00:00"))
        end_time = start_time  # For imported logs, assume minimal execution time

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO agent_tasks (
                    task_id, agent_type, task_description, start_time, end_time,
                    execution_result, error_category, execution_time_ms, retry_count,
                    error_message, stack_trace, command, working_directory,
                    environment_state
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    task_id,
                    execution_log.agent_type,
                    execution_log.task_description,
                    start_time,
                    end_time,
                    execution_log.execution_result,
                    execution_log.error_category,
                    execution_log.execution_time_ms,
                    execution_log.retry_count,
                    execution_log.error_message,
                    execution_log.stack_trace,
                    execution_log.command,
                    execution_log.working_directory,
                    json.dumps(execution_log.environment_state),
                ),
            )

            conn.commit()

        return task_id


# Global task tracker instance
_global_tracker = None


def get_tracker() -> AgentTaskTracker:
    """Get global task tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = AgentTaskTracker()
    return _global_tracker
