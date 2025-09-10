#!/usr/bin/env python3
"""
Sub-Agent Timeout and Interruption Handler
Monitors and recovers from agent execution failures in CI/CD workflows
"""

import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class AgentExecutionResult:
    """Result of agent task execution"""

    agent_type: str
    task_description: str
    success: bool
    execution_time: float
    error_message: Optional[str] = None
    recovery_attempted: bool = False
    retry_count: int = 0


class SubAgentTimeoutHandler:
    """Handles sub-agent timeouts and execution failures"""

    def __init__(self, config_path: str = "common/config/agent_error_handling.yml"):
        self.config_path = config_path
        self.logger = self._setup_logging()
        self.max_retries = 3
        self.timeout_seconds = 300  # 5 minutes default
        self.circuit_breaker_failures = {}

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for agent execution monitoring"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("logs/agent-execution.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        return logging.getLogger(__name__)

    def execute_with_timeout(
        self,
        agent_type: str,
        task_description: str,
        command: List[str],
        timeout_override: Optional[int] = None,
    ) -> AgentExecutionResult:
        """Execute agent task with timeout and recovery handling"""

        timeout = timeout_override or self.timeout_seconds
        start_time = time.time()

        # Check circuit breaker
        if self._is_circuit_breaker_open(agent_type):
            self.logger.warning(f"🚨 Circuit breaker OPEN for {agent_type} - skipping execution")
            return AgentExecutionResult(
                agent_type=agent_type,
                task_description=task_description,
                success=False,
                execution_time=0.0,
                error_message="Circuit breaker is open - too many recent failures",
            )

        for attempt in range(self.max_retries):
            try:
                self.logger.info(
                    f"🚀 Executing {agent_type} (attempt {attempt + 1}/{self.max_retries})"
                )
                self.logger.info(f"📝 Task: {task_description}")
                self.logger.info(f"⏰ Timeout: {timeout}s")

                # Execute with timeout
                result = subprocess.run(
                    command, timeout=timeout, capture_output=True, text=True, check=False
                )

                execution_time = time.time() - start_time

                if result.returncode == 0:
                    self.logger.info(
                        f"✅ {agent_type} completed successfully in {execution_time:.2f}s"
                    )
                    self._record_success(agent_type)
                    return AgentExecutionResult(
                        agent_type=agent_type,
                        task_description=task_description,
                        success=True,
                        execution_time=execution_time,
                        retry_count=attempt,
                    )
                else:
                    error_msg = result.stderr or result.stdout or "Unknown error"
                    self.logger.error(f"❌ {agent_type} failed (exit code {result.returncode})")
                    self.logger.error(f"🔍 Error: {error_msg}")

                    # Check if we should retry
                    if not self._should_retry(error_msg, attempt):
                        break

                    # Wait before retry with exponential backoff
                    wait_time = min(2**attempt, 30)  # Cap at 30 seconds
                    self.logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)

            except subprocess.TimeoutExpired:
                execution_time = time.time() - start_time
                self.logger.error(f"⏰ {agent_type} timed out after {timeout}s")

                # Try recovery actions
                if attempt < self.max_retries - 1:
                    self._attempt_recovery(agent_type)
                    continue

                self._record_failure(agent_type)
                return AgentExecutionResult(
                    agent_type=agent_type,
                    task_description=task_description,
                    success=False,
                    execution_time=execution_time,
                    error_message=f"Timeout after {timeout}s",
                    retry_count=attempt + 1,
                )

            except Exception as e:
                execution_time = time.time() - start_time
                self.logger.error(f"💥 Unexpected error in {agent_type}: {str(e)}")

                if attempt < self.max_retries - 1:
                    continue

                self._record_failure(agent_type)
                return AgentExecutionResult(
                    agent_type=agent_type,
                    task_description=task_description,
                    success=False,
                    execution_time=execution_time,
                    error_message=str(e),
                    retry_count=attempt + 1,
                )

        # All retries exhausted
        self._record_failure(agent_type)
        return AgentExecutionResult(
            agent_type=agent_type,
            task_description=task_description,
            success=False,
            execution_time=time.time() - start_time,
            error_message="All retry attempts exhausted",
            retry_count=self.max_retries,
        )

    def _should_retry(self, error_message: str, attempt: int) -> bool:
        """Determine if we should retry based on error type"""
        # Don't retry on final attempt
        if attempt >= self.max_retries - 1:
            return False

        # Retry on transient errors
        transient_errors = [
            "connection timeout",
            "connection refused",
            "network unreachable",
            "temporary failure",
            "resource temporarily unavailable",
            "database connection",
            "rate limit",
        ]

        error_lower = error_message.lower()
        return any(err in error_lower for err in transient_errors)

    def _attempt_recovery(self, agent_type: str):
        """Attempt to recover from agent failure"""
        self.logger.info(f"🔧 Attempting recovery for {agent_type}...")

        recovery_actions = {
            "backend-architect-agent": self._recover_database_connections,
            "data-engineer-agent": self._recover_data_pipeline,
            "web-backend-agent": self._recover_api_services,
            "default": self._generic_recovery,
        }

        recovery_action = recovery_actions.get(agent_type, recovery_actions["default"])

        try:
            recovery_action()
            self.logger.info(f"✅ Recovery attempted for {agent_type}")
        except Exception as e:
            self.logger.error(f"❌ Recovery failed for {agent_type}: {str(e)}")

    def _recover_database_connections(self):
        """Specific recovery for database connection issues"""
        self.logger.info("🔄 Resetting database connections...")
        # Add database connection reset logic here
        time.sleep(2)  # Allow connections to reset

    def _recover_data_pipeline(self):
        """Specific recovery for data pipeline issues"""
        self.logger.info("🔄 Clearing data pipeline locks...")
        # Add pipeline reset logic here
        time.sleep(1)

    def _recover_api_services(self):
        """Specific recovery for API service issues"""
        self.logger.info("🔄 Refreshing API connections...")
        # Add API connection refresh logic here
        time.sleep(1)

    def _generic_recovery(self):
        """Generic recovery actions"""
        self.logger.info("🔄 Performing generic recovery...")
        time.sleep(1)

    def _is_circuit_breaker_open(self, agent_type: str) -> bool:
        """Check if circuit breaker is open for this agent"""
        failure_info = self.circuit_breaker_failures.get(agent_type)
        if not failure_info:
            return False

        # Open circuit if too many failures in recent time
        failure_count = failure_info.get("count", 0)
        last_failure = failure_info.get("last_failure")

        if failure_count >= 5 and last_failure:
            # Keep circuit open for 10 minutes after 5 failures
            if datetime.now() - last_failure < timedelta(minutes=10):
                return True

        return False

    def _record_success(self, agent_type: str):
        """Record successful execution"""
        # Reset failure count on success
        if agent_type in self.circuit_breaker_failures:
            del self.circuit_breaker_failures[agent_type]

    def _record_failure(self, agent_type: str):
        """Record failed execution for circuit breaker"""
        if agent_type not in self.circuit_breaker_failures:
            self.circuit_breaker_failures[agent_type] = {"count": 0}

        self.circuit_breaker_failures[agent_type]["count"] += 1
        self.circuit_breaker_failures[agent_type]["last_failure"] = datetime.now()

        count = self.circuit_breaker_failures[agent_type]["count"]
        self.logger.warning(f"⚠️ Recorded failure #{count} for {agent_type}")

        if count >= 5:
            self.logger.error(f"🚨 Circuit breaker OPENED for {agent_type} - too many failures")


def main():
    """CLI interface for the timeout handler"""
    if len(sys.argv) < 4:
        print("Usage: agent-timeout-handler.py <agent_type> <task_description> <command...>")
        sys.exit(1)

    agent_type = sys.argv[1]
    task_description = sys.argv[2]
    command = sys.argv[3:]

    handler = SubAgentTimeoutHandler()
    result = handler.execute_with_timeout(agent_type, task_description, command)

    # Output result as JSON for consumption by CI
    print(
        json.dumps(
            {
                "success": result.success,
                "agent_type": result.agent_type,
                "execution_time": result.execution_time,
                "error_message": result.error_message,
                "retry_count": result.retry_count,
            }
        )
    )

    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
