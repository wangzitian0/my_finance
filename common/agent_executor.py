#!/usr/bin/env python3
"""
Resilient Agent Execution System

Provides a robust execution wrapper that integrates circuit breaker,
retry logic, and task interruption for sub-agent operations.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from .error_recovery import (
    CircuitState,
    TaskState,
    get_circuit_breaker,
    get_retry_manager,
    get_task_manager,
)


@dataclass
class AgentExecutionResult:
    """Result of agent execution with metadata."""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    agent_type: str = ""
    task_id: str = ""
    execution_time: float = 0.0
    retry_count: int = 0
    circuit_tripped: bool = False


class AgentExecutionError(Exception):
    """Custom exception for agent execution failures."""
    
    def __init__(
        self,
        message: str,
        agent_type: str,
        task_id: str,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.agent_type = agent_type
        self.task_id = task_id
        self.original_error = original_error


class ResilientAgentExecutor:
    """
    Resilient agent execution system with integrated error recovery.
    
    Combines circuit breaker, retry logic, and task interruption for
    robust sub-agent operations with comprehensive error handling.
    """
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.circuit_breaker = get_circuit_breaker(agent_type)
        self.retry_manager = get_retry_manager(agent_type)
        self.task_manager = get_task_manager()
        
        self.logger = logging.getLogger(f"agent_executor.{agent_type}")
    
    async def execute(self,
                     func: Callable,
                     task_description: str,
                     context: Optional[Dict[str, Any]] = None,
                     timeout: Optional[float] = None,
                     *args,
                     **kwargs) -> AgentExecutionResult:
        """
        Execute function with full error recovery system.
        
        Args:
            func: Function to execute
            task_description: Human-readable task description  
            context: Optional context for checkpointing
            timeout: Optional custom timeout (default: 120s)
            *args, **kwargs: Arguments for function
            
        Returns:
            AgentExecutionResult with execution metadata
        """
        task_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Create task checkpoint
        checkpoint = self.task_manager.create_task(
            task_id=task_id,
            agent_type=self.agent_type,
            context={
                "description": task_description,
                "args": str(args),
                "kwargs": {k: str(v) for k, v in kwargs.items()},
                **(context or {})
            }
        )
        
        try:
            # Check circuit breaker
            if not self.circuit_breaker.can_execute():
                self.logger.warning(
                    f"Circuit breaker OPEN for {self.agent_type}, execution blocked"
                )
                return AgentExecutionResult(
                    success=False,
                    error=AgentExecutionError(
                        f"Circuit breaker is OPEN for {self.agent_type}",
                        self.agent_type,
                        task_id
                    ),
                    agent_type=self.agent_type,
                    task_id=task_id,
                    execution_time=time.time() - start_time,
                    circuit_tripped=True
                )
            
            # Start task
            self.task_manager.start_task(task_id)
            self.logger.info(f"Starting task {task_id}: {task_description}")
            
            # Execute with retry and timeout
            result = await self._execute_with_recovery(
                func, task_id, timeout or 120.0, *args, **kwargs
            )
            
            # Record success
            self.circuit_breaker.record_success()
            self.task_manager.complete_task(task_id, success=True)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Task {task_id} completed successfully in {execution_time:.2f}s")
            
            return AgentExecutionResult(
                success=True,
                result=result,
                agent_type=self.agent_type,
                task_id=task_id,
                execution_time=execution_time
            )
            
        except Exception as e:
            # Record failure
            self.circuit_breaker.record_failure()
            self.task_manager.complete_task(task_id, success=False)
            
            execution_time = time.time() - start_time
            self.logger.error(f"Task {task_id} failed after {execution_time:.2f}s: {str(e)}")
            
            return AgentExecutionResult(
                success=False,
                error=e if isinstance(e, AgentExecutionError) else AgentExecutionError(
                    str(e), self.agent_type, task_id, e
                ),
                agent_type=self.agent_type,
                task_id=task_id,
                execution_time=execution_time
            )
    
    async def _execute_with_recovery(self,
                                   func: Callable,
                                   task_id: str,
                                   timeout: float,
                                   *args,
                                   **kwargs) -> Any:
        """Execute function with retry logic and timeout monitoring."""
        
        async def monitored_execution():
            """Wrapper that monitors for interruption signals."""
            # Create task with timeout
            execution_task = asyncio.create_task(
                self.retry_manager.execute_with_retry(func, *args, **kwargs)
            )
            
            # Monitor for interruption
            while not execution_task.done():
                if self.task_manager.should_interrupt(task_id):
                    execution_task.cancel()
                    raise AgentExecutionError(
                        "Task was interrupted",
                        self.agent_type,
                        task_id
                    )
                
                # Update checkpoint periodically
                self.task_manager.update_checkpoint(task_id, {
                    "status": "executing",
                    "timestamp": time.time()
                })
                
                await asyncio.sleep(0.1)
            
            return await execution_task
        
        # Execute with timeout
        try:
            return await asyncio.wait_for(monitored_execution(), timeout=timeout)
        except asyncio.TimeoutError:
            self.task_manager.interrupt_task(task_id)
            raise AgentExecutionError(
                f"Task timed out after {timeout}s",
                self.agent_type,
                task_id
            )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for this agent executor."""
        return {
            "agent_type": self.agent_type,
            "circuit_breaker": self.circuit_breaker.get_status(),
            "retry_stats": self.retry_manager.get_stats(),
            "can_execute": self.circuit_breaker.can_execute()
        }


class AgentCoordinatorIntegration:
    """
    Integration layer for agent-coordinator with error recovery.
    
    Provides enhanced delegation with resilience patterns and
    comprehensive error handling for multi-agent workflows.
    """
    
    def __init__(self):
        self.executors: Dict[str, ResilientAgentExecutor] = {}
        self.logger = logging.getLogger("agent_coordinator_integration")
    
    def get_executor(self, agent_type: str) -> ResilientAgentExecutor:
        """Get or create resilient executor for agent type."""
        if agent_type not in self.executors:
            self.executors[agent_type] = ResilientAgentExecutor(agent_type)
        return self.executors[agent_type]
    
    async def delegate_task(self,
                           agent_type: str,
                           func: Callable,
                           task_description: str,
                           context: Optional[Dict[str, Any]] = None,
                           fallback_agent: Optional[str] = None,
                           *args,
                           **kwargs) -> AgentExecutionResult:
        """
        Delegate task to agent with fallback support.
        
        Args:
            agent_type: Primary agent to execute task
            func: Function to execute
            task_description: Human-readable task description
            context: Optional context for checkpointing
            fallback_agent: Optional fallback agent if primary fails
            *args, **kwargs: Arguments for function
            
        Returns:
            AgentExecutionResult with execution metadata
        """
        executor = self.get_executor(agent_type)
        
        # Try primary agent
        result = await executor.execute(
            func, task_description, context, None, *args, **kwargs
        )
        
        # If primary fails and fallback available, try fallback
        if not result.success and fallback_agent and fallback_agent != agent_type:
            self.logger.warning(
                f"Primary agent {agent_type} failed, trying fallback {fallback_agent}"
            )
            
            fallback_executor = self.get_executor(fallback_agent)
            fallback_result = await fallback_executor.execute(
                func, f"[FALLBACK] {task_description}", context, None, *args, **kwargs
            )
            
            if fallback_result.success:
                self.logger.info(
                    f"Fallback agent {fallback_agent} succeeded where {agent_type} failed"
                )
                return fallback_result
        
        return result
    
    async def parallel_execution(self,
                                tasks: List[Tuple[str, Callable, str, Optional[Dict[str, Any]]]],
                                timeout: Optional[float] = None) -> List[AgentExecutionResult]:
        """
        Execute multiple tasks in parallel with error recovery.
        
        Args:
            tasks: List of (agent_type, func, description, context) tuples
            timeout: Optional timeout for all tasks
            
        Returns:
            List of AgentExecutionResults
        """
        execution_tasks = []
        
        for agent_type, func, description, context in tasks:
            executor = self.get_executor(agent_type)
            task = executor.execute(func, description, context)
            execution_tasks.append(task)
        
        # Execute all tasks in parallel
        if timeout:
            results = await asyncio.wait_for(
                asyncio.gather(*execution_tasks, return_exceptions=True),
                timeout=timeout
            )
        else:
            results = await asyncio.gather(*execution_tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_type = tasks[i][0]
                processed_results.append(AgentExecutionResult(
                    success=False,
                    error=result,
                    agent_type=agent_type,
                    task_id=str(uuid.uuid4()),
                    execution_time=0.0
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        executor_health = {
            agent_type: executor.get_health_status()
            for agent_type, executor in self.executors.items()
        }
        
        # Overall system health
        healthy_agents = sum(
            1 for health in executor_health.values()
            if health["can_execute"]
        )
        total_agents = len(executor_health)
        
        return {
            "agent_executors": executor_health,
            "healthy_agents": healthy_agents,
            "total_agents": total_agents,
            "system_health_percentage": (
                (healthy_agents / total_agents * 100) if total_agents > 0 else 100
            ),
            "timestamp": time.time()
        }


# Global coordinator integration instance
_coordinator_integration = AgentCoordinatorIntegration()


def get_coordinator_integration() -> AgentCoordinatorIntegration:
    """Get the global coordinator integration instance."""
    return _coordinator_integration


async def resilient_agent_call(agent_type: str,
                             func: Callable,
                             task_description: str,
                             context: Optional[Dict[str, Any]] = None,
                             *args,
                             **kwargs) -> AgentExecutionResult:
    """
    Convenience function for resilient agent execution.
    
    Args:
        agent_type: Agent type to execute task
        func: Function to execute
        task_description: Human-readable task description  
        context: Optional context for checkpointing
        *args, **kwargs: Arguments for function
        
    Returns:
        AgentExecutionResult with execution metadata
    """
    coordinator = get_coordinator_integration()
    return await coordinator.delegate_task(
        agent_type, func, task_description, context, *args, **kwargs
    )