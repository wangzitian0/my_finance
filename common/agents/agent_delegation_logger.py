#!/usr/bin/env python3
"""
Agent Delegation Logging Utility

Provides logging capabilities for agent-coordinator delegations and
inter-agent communication as part of the Agent Execution Monitoring System.
"""
import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agent_task_tracker import get_tracker
from .execution_monitor import ExecutionResult, get_monitor


@dataclass
class AgentDelegation:
    """Agent delegation record."""

    delegation_id: str
    from_agent: str
    to_agent: str
    task_description: str
    task_parameters: Dict[str, Any]
    timestamp: str
    status: str  # pending, in_progress, completed, failed
    result: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None


class AgentDelegationLogger:
    """
    Logger for agent delegations and inter-agent communications.

    Tracks all agent-coordinator delegations and provides metrics
    for delegation patterns and agent performance analysis.
    """

    def __init__(self, log_directory: Optional[Path] = None):
        """Initialize delegation logger."""
        if log_directory is None:
            # Use centralized DirectoryManager for SSOT compliance
            from ..core.directory_manager import directory_manager

            self.log_directory = directory_manager.get_logs_path()
        else:
            self.log_directory = Path(log_directory)

        self._active_delegations = {}

    def start_delegation(
        self,
        from_agent: str,
        to_agent: str,
        task_description: str,
        task_parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Start logging an agent delegation.

        Args:
            from_agent: Agent making the delegation
            to_agent: Agent receiving the task
            task_description: Description of the delegated task
            task_parameters: Task parameters and context

        Returns:
            str: Delegation ID for tracking
        """
        import uuid

        delegation_id = str(uuid.uuid4())

        delegation = AgentDelegation(
            delegation_id=delegation_id,
            from_agent=from_agent,
            to_agent=to_agent,
            task_description=task_description,
            task_parameters=task_parameters or {},
            timestamp=datetime.now().isoformat(),
            status="pending",
        )

        self._active_delegations[delegation_id] = {
            "delegation": delegation,
            "start_time": time.time(),
        }

        # Log to execution monitor
        monitor = get_monitor()
        monitor.start_execution(
            agent_type=f"delegation-{from_agent}-to-{to_agent}",
            task_description=task_description,
            command=f"delegate-to-{to_agent}",
        )

        # Log to task tracker
        tracker = get_tracker()
        tracker.create_task(
            agent_type=f"delegation-{from_agent}-to-{to_agent}",
            task_description=task_description,
            command=f"delegate-to-{to_agent}",
        )

        self._save_delegation(delegation)

        print(f"🔗 Agent delegation started: {from_agent} → {to_agent}")
        print(f"   Task: {task_description}")
        print(f"   Delegation ID: {delegation_id}")

        return delegation_id

    def complete_delegation(
        self,
        delegation_id: str,
        success: bool,
        result: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """
        Complete an agent delegation.

        Args:
            delegation_id: ID of the delegation to complete
            success: Whether the delegation succeeded
            result: Result summary if successful
            error_message: Error message if failed
        """
        if delegation_id not in self._active_delegations:
            print(f"⚠️  Delegation {delegation_id} not found in active delegations")
            return

        delegation_info = self._active_delegations[delegation_id]
        delegation = delegation_info["delegation"]
        start_time = delegation_info["start_time"]

        # Update delegation record
        execution_time_ms = int((time.time() - start_time) * 1000)
        delegation.execution_time_ms = execution_time_ms
        delegation.status = "completed" if success else "failed"
        delegation.result = result
        delegation.error_message = error_message

        # Log to execution monitor
        monitor = get_monitor()
        if success:
            monitor.log_execution(ExecutionResult.SUCCESS)
        else:
            monitor.log_execution(ExecutionResult.FAILURE, error_message=error_message)

        # Save updated delegation
        self._save_delegation(delegation)

        # Remove from active delegations
        del self._active_delegations[delegation_id]

        if success:
            print(f"✅ Delegation completed: {delegation.from_agent} → {delegation.to_agent}")
            print(f"   Time: {execution_time_ms}ms")
        else:
            print(f"❌ Delegation failed: {delegation.from_agent} → {delegation.to_agent}")
            print(f"   Error: {error_message}")

    def _save_delegation(self, delegation: AgentDelegation):
        """Save delegation record to JSON file."""
        # Create daily delegation files
        log_date = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_directory / f"agent_delegations_{log_date}.json"

        # Load existing delegations
        delegations = []
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    delegations = json.load(f)
            except json.JSONDecodeError:
                delegations = []

        # Find and update existing delegation or add new one
        delegation_dict = {
            "delegation_id": delegation.delegation_id,
            "from_agent": delegation.from_agent,
            "to_agent": delegation.to_agent,
            "task_description": delegation.task_description,
            "task_parameters": delegation.task_parameters,
            "timestamp": delegation.timestamp,
            "status": delegation.status,
            "result": delegation.result,
            "error_message": delegation.error_message,
            "execution_time_ms": delegation.execution_time_ms,
        }

        # Update existing or append new
        updated = False
        for i, existing in enumerate(delegations):
            if existing["delegation_id"] == delegation.delegation_id:
                delegations[i] = delegation_dict
                updated = True
                break

        if not updated:
            delegations.append(delegation_dict)

        # Save updated delegations
        try:
            with open(log_file, "w") as f:
                json.dump(delegations, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save delegation log: {e}")

    def get_delegation_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Get delegation statistics for the last N days.

        Args:
            days: Number of days to analyze

        Returns:
            Dict with delegation statistics
        """
        from datetime import timedelta

        stats = {
            "total_delegations": 0,
            "successful_delegations": 0,
            "failed_delegations": 0,
            "avg_execution_time_ms": 0,
            "delegation_patterns": {},
            "agent_utilization": {},
            "most_delegated_to": {},
            "busiest_coordinators": {},
        }

        # Collect delegation logs from the last N days
        all_delegations = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            log_date = date.strftime("%Y-%m-%d")
            log_file = self.log_directory / f"agent_delegations_{log_date}.json"

            if log_file.exists():
                try:
                    with open(log_file, "r") as f:
                        daily_delegations = json.load(f)
                        all_delegations.extend(daily_delegations)
                except json.JSONDecodeError:
                    continue

        if not all_delegations:
            return stats

        # Calculate statistics
        stats["total_delegations"] = len(all_delegations)
        execution_times = []

        for delegation in all_delegations:
            if delegation["status"] == "completed":
                stats["successful_delegations"] += 1
            elif delegation["status"] == "failed":
                stats["failed_delegations"] += 1

            if delegation["execution_time_ms"]:
                execution_times.append(delegation["execution_time_ms"])

            # Delegation patterns
            pattern = f"{delegation['from_agent']} → {delegation['to_agent']}"
            stats["delegation_patterns"][pattern] = stats["delegation_patterns"].get(pattern, 0) + 1

            # Agent utilization (who receives most delegations)
            to_agent = delegation["to_agent"]
            stats["most_delegated_to"][to_agent] = stats["most_delegated_to"].get(to_agent, 0) + 1

            # Coordinator utilization (who delegates most)
            from_agent = delegation["from_agent"]
            stats["busiest_coordinators"][from_agent] = (
                stats["busiest_coordinators"].get(from_agent, 0) + 1
            )

        # Calculate averages
        if execution_times:
            stats["avg_execution_time_ms"] = sum(execution_times) / len(execution_times)

        # Success rate
        total = stats["total_delegations"]
        stats["success_rate"] = stats["successful_delegations"] / total if total > 0 else 0

        return stats


# Global delegation logger instance
_global_delegation_logger = None


def get_delegation_logger() -> AgentDelegationLogger:
    """Get global delegation logger instance."""
    global _global_delegation_logger
    if _global_delegation_logger is None:
        _global_delegation_logger = AgentDelegationLogger()
    return _global_delegation_logger


# Convenience functions for agent use
def log_delegation_start(
    from_agent: str,
    to_agent: str,
    task_description: str,
    task_parameters: Optional[Dict[str, Any]] = None,
) -> str:
    """Start logging an agent delegation."""
    logger = get_delegation_logger()
    return logger.start_delegation(from_agent, to_agent, task_description, task_parameters)


def log_delegation_success(delegation_id: str, result: Optional[str] = None):
    """Log successful delegation completion."""
    logger = get_delegation_logger()
    logger.complete_delegation(delegation_id, success=True, result=result)


def log_delegation_failure(delegation_id: str, error_message: str):
    """Log failed delegation."""
    logger = get_delegation_logger()
    logger.complete_delegation(delegation_id, success=False, error_message=error_message)


def delegation_context(from_agent: str, to_agent: str, task_description: str):
    """
    Context manager for tracking agent delegations.

    Usage:
        with delegation_context("agent-coordinator", "git-ops-agent", "Create PR"):
            # delegation work here
            pass
    """

    class DelegationContext:
        def __init__(self, from_agent: str, to_agent: str, task_description: str):
            self.from_agent = from_agent
            self.to_agent = to_agent
            self.task_description = task_description
            self.delegation_id = None

        def __enter__(self):
            self.delegation_id = log_delegation_start(
                self.from_agent, self.to_agent, self.task_description
            )
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                log_delegation_success(self.delegation_id)
            else:
                log_delegation_failure(self.delegation_id, str(exc_val))

    return DelegationContext(from_agent, to_agent, task_description)
