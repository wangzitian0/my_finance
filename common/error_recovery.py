#!/usr/bin/env python3
"""
Sub-Agent Error Recovery & Resilience System

Implements circuit breaker, adaptive retry, and task interruption patterns
for robust sub-agent execution with graceful error handling.
"""

import asyncio
import logging
import random
import signal
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from threading import Event, Lock, Thread
from typing import Any, Callable, Dict, List, Optional, Tuple


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"


class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 2
    timeout_seconds: float = 120.0


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter_factor: float = 0.1


@dataclass
class TaskCheckpoint:
    task_id: str
    agent_type: str
    state: TaskState
    created_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    error_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)


class SubAgentCircuitBreaker:
    """
    Circuit breaker pattern implementation for sub-agent execution.
    
    Manages circuit states (closed/open/half-open) with configurable failure
    thresholds and recovery timeouts to prevent cascading failures.
    """
    
    def __init__(self, agent_type: str, config: Optional[CircuitBreakerConfig] = None):
        self.agent_type = agent_type
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self.lock = Lock()
        
        # Success history for pattern analysis
        self.success_history: List[bool] = []
        self.max_history_size = 100
        
        self.logger = logging.getLogger(f"circuit_breaker.{agent_type}")
    
    def can_execute(self) -> bool:
        """Check if the circuit allows execution."""
        with self.lock:
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    self.logger.info(
                        f"Circuit breaker transitioning to HALF_OPEN for {self.agent_type}"
                    )
                    return True
                return False
            elif self.state == CircuitState.HALF_OPEN:
                return True
            return False
    
    def record_success(self):
        """Record a successful execution."""
        with self.lock:
            self.success_history.append(True)
            self._trim_history()
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.logger.info(f"Circuit breaker CLOSED for {self.agent_type}")
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0
    
    def record_failure(self):
        """Record a failed execution."""
        with self.lock:
            self.success_history.append(False)
            self._trim_history()
            
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN]:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    self.logger.warning(
                        f"Circuit breaker OPENED for {self.agent_type} "
                        f"after {self.failure_count} failures"
                    )
    
    def get_success_rate(self) -> float:
        """Calculate recent success rate for pattern analysis."""
        if not self.success_history:
            return 1.0
        return sum(self.success_history) / len(self.success_history)
    
    def _trim_history(self):
        """Keep history within size limits."""
        if len(self.success_history) > self.max_history_size:
            self.success_history = self.success_history[-self.max_history_size:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "agent_type": self.agent_type,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "success_rate": self.get_success_rate(),
            "last_failure_time": self.last_failure_time
        }


class AdaptiveRetryManager:
    """
    Adaptive retry system with exponential backoff and jitter.
    
    Analyzes historical success patterns to optimize retry strategies
    and prevent "thundering herd" effects.
    """
    
    def __init__(self, agent_type: str, config: Optional[RetryConfig] = None):
        self.agent_type = agent_type
        self.config = config or RetryConfig()
        self.execution_history: List[Tuple[bool, float]] = []  # (success, duration)
        self.lock = Lock()
        
        self.logger = logging.getLogger(f"retry_manager.{agent_type}")
    
    async def execute_with_retry(self, 
                                func: Callable,
                                *args,
                                **kwargs) -> Any:
        """Execute function with adaptive retry logic."""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                start_time = time.time()
                result = await self._execute_function(func, *args, **kwargs)
                duration = time.time() - start_time
                
                self._record_execution(True, duration)
                self.logger.debug(
                    f"Successful execution on attempt {attempt + 1} for {self.agent_type}"
                )
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                self._record_execution(False, duration)
                last_exception = e
                
                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_retry_delay(attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed for {self.agent_type}, "
                        f"retrying in {delay:.2f}s: {str(e)}"
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(
                        f"All {self.config.max_attempts} attempts failed for {self.agent_type}"
                    )
        
        raise last_exception
    
    async def _execute_function(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function, handling both sync and async."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate adaptive delay with exponential backoff and jitter."""
        base_delay = min(
            self.config.base_delay * (self.config.backoff_multiplier ** attempt),
            self.config.max_delay
        )
        
        # Add jitter to prevent thundering herd
        jitter = base_delay * self.config.jitter_factor * (random.random() * 2 - 1)
        delay = base_delay + jitter
        
        # Adjust based on historical patterns
        success_rate = self._get_recent_success_rate()
        if success_rate < 0.5:
            delay *= 1.5  # Slower retry for consistently failing operations
        
        return max(0.1, delay)  # Minimum delay of 100ms
    
    def _record_execution(self, success: bool, duration: float):
        """Record execution result for pattern analysis."""
        with self.lock:
            self.execution_history.append((success, duration))
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-100:]
    
    def _get_recent_success_rate(self) -> float:
        """Calculate recent success rate for adaptive behavior."""
        if not self.execution_history:
            return 1.0
        
        recent_results = self.execution_history[-20:]  # Last 20 executions
        if not recent_results:
            return 1.0
        
        successes = sum(1 for success, _ in recent_results if success)
        return successes / len(recent_results)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {
                "agent_type": self.agent_type,
                "total_executions": 0,
                "success_rate": 1.0,
                "avg_duration": 0.0
            }
        
        total = len(self.execution_history)
        successes = sum(1 for success, _ in self.execution_history if success)
        avg_duration = sum(duration for _, duration in self.execution_history) / total
        
        return {
            "agent_type": self.agent_type,
            "total_executions": total,
            "success_rate": successes / total,
            "avg_duration": avg_duration,
            "recent_success_rate": self._get_recent_success_rate()
        }


class TaskInterruptionManager:
    """
    Task interruption and recovery manager with 120-second timeout.
    
    Provides graceful task termination with checkpoint-based recovery
    and 5-second interruption response time.
    """
    
    def __init__(self):
        self.active_tasks: Dict[str, TaskCheckpoint] = {}
        self.lock = Lock()
        self.interrupt_events: Dict[str, Event] = {}
        
        # Global timeout monitoring
        self.monitor_thread = Thread(target=self._monitor_tasks, daemon=True)
        self.monitor_running = True
        self.monitor_thread.start()
        
        self.logger = logging.getLogger("task_interruption_manager")
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
    
    def create_task(self, task_id: str, agent_type: str, context: Optional[Dict[str, Any]] = None) -> TaskCheckpoint:
        """Create a new task with checkpoint."""
        checkpoint = TaskCheckpoint(
            task_id=task_id,
            agent_type=agent_type,
            state=TaskState.PENDING,
            context=context or {}
        )
        
        with self.lock:
            self.active_tasks[task_id] = checkpoint
            self.interrupt_events[task_id] = Event()
        
        self.logger.debug(f"Created task {task_id} for {agent_type}")
        return checkpoint
    
    def start_task(self, task_id: str) -> bool:
        """Mark task as running."""
        with self.lock:
            if task_id in self.active_tasks:
                self.active_tasks[task_id].state = TaskState.RUNNING
                self.active_tasks[task_id].last_update = time.time()
                self.logger.debug(f"Started task {task_id}")
                return True
        return False
    
    def complete_task(self, task_id: str, success: bool = True) -> bool:
        """Mark task as completed or failed."""
        with self.lock:
            if task_id in self.active_tasks:
                self.active_tasks[task_id].state = TaskState.COMPLETED if success else TaskState.FAILED
                self.active_tasks[task_id].last_update = time.time()
                
                # Clean up interrupt event
                if task_id in self.interrupt_events:
                    del self.interrupt_events[task_id]
                
                self.logger.debug(f"Completed task {task_id} with success={success}")
                return True
        return False
    
    def interrupt_task(self, task_id: str, timeout: float = 5.0) -> bool:
        """Interrupt task with graceful termination."""
        with self.lock:
            if task_id not in self.active_tasks:
                return False
            
            if task_id not in self.interrupt_events:
                return False
            
            self.active_tasks[task_id].state = TaskState.INTERRUPTED
            self.active_tasks[task_id].last_update = time.time()
            
            # Signal task to stop
            interrupt_event = self.interrupt_events[task_id]
        
        # Set interrupt signal
        interrupt_event.set()
        
        # Wait for graceful termination
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self.lock:
                if (task_id not in self.active_tasks or 
                    self.active_tasks[task_id].state in [TaskState.COMPLETED, TaskState.FAILED]):
                    self.logger.info(f"Task {task_id} terminated gracefully")
                    return True
            time.sleep(0.1)
        
        self.logger.warning(f"Task {task_id} did not respond to interrupt within {timeout}s")
        return False
    
    def should_interrupt(self, task_id: str) -> bool:
        """Check if task should be interrupted."""
        if task_id in self.interrupt_events:
            return self.interrupt_events[task_id].is_set()
        return False
    
    def update_checkpoint(self, task_id: str, context: Dict[str, Any]) -> bool:
        """Update task checkpoint with current context."""
        with self.lock:
            if task_id in self.active_tasks:
                self.active_tasks[task_id].context.update(context)
                self.active_tasks[task_id].last_update = time.time()
                return True
        return False
    
    def get_checkpoint(self, task_id: str) -> Optional[TaskCheckpoint]:
        """Get task checkpoint for recovery."""
        with self.lock:
            return self.active_tasks.get(task_id)
    
    def _monitor_tasks(self):
        """Monitor tasks for timeouts (120-second default)."""
        while self.monitor_running:
            current_time = time.time()
            timeout_tasks = []
            
            with self.lock:
                for task_id, checkpoint in self.active_tasks.items():
                    if (checkpoint.state == TaskState.RUNNING and 
                        current_time - checkpoint.last_update > 120.0):
                        timeout_tasks.append(task_id)
            
            # Interrupt timed-out tasks
            for task_id in timeout_tasks:
                self.logger.warning(f"Task {task_id} timed out after 120 seconds, interrupting")
                self.interrupt_task(task_id)
            
            time.sleep(1.0)
    
    def _handle_shutdown(self, signum, frame):
        """Handle graceful shutdown."""
        self.logger.info("Received shutdown signal, terminating active tasks")
        self.monitor_running = False
        
        with self.lock:
            active_task_ids = list(self.active_tasks.keys())
        
        for task_id in active_task_ids:
            self.interrupt_task(task_id, timeout=2.0)
        
        sys.exit(0)
    
    def get_active_tasks(self) -> List[TaskCheckpoint]:
        """Get all active tasks."""
        with self.lock:
            return list(self.active_tasks.values())
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24) -> int:
        """Clean up old completed tasks."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        removed_count = 0
        
        with self.lock:
            to_remove = []
            for task_id, checkpoint in self.active_tasks.items():
                if (checkpoint.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.INTERRUPTED] and
                    checkpoint.last_update < cutoff_time):
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.active_tasks[task_id]
                if task_id in self.interrupt_events:
                    del self.interrupt_events[task_id]
                removed_count += 1
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} completed tasks")
        
        return removed_count


# Global instances for system-wide use
_circuit_breakers: Dict[str, SubAgentCircuitBreaker] = {}
_retry_managers: Dict[str, AdaptiveRetryManager] = {}
_task_manager = TaskInterruptionManager()


def get_circuit_breaker(agent_type: str) -> SubAgentCircuitBreaker:
    """Get or create circuit breaker for agent type."""
    if agent_type not in _circuit_breakers:
        _circuit_breakers[agent_type] = SubAgentCircuitBreaker(agent_type)
    return _circuit_breakers[agent_type]


def get_retry_manager(agent_type: str) -> AdaptiveRetryManager:
    """Get or create retry manager for agent type."""
    if agent_type not in _retry_managers:
        _retry_managers[agent_type] = AdaptiveRetryManager(agent_type)
    return _retry_managers[agent_type]


def get_task_manager() -> TaskInterruptionManager:
    """Get the global task interruption manager."""
    return _task_manager


def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status for monitoring."""
    circuit_status = {
        agent_type: breaker.get_status()
        for agent_type, breaker in _circuit_breakers.items()
    }
    
    retry_status = {
        agent_type: manager.get_stats()
        for agent_type, manager in _retry_managers.items()
    }
    
    active_tasks = len(_task_manager.get_active_tasks())
    
    return {
        "circuit_breakers": circuit_status,
        "retry_managers": retry_status,
        "active_tasks": active_tasks,
        "timestamp": time.time()
    }