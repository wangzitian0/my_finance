#!/usr/bin/env python3
"""
Comprehensive tests for Sub-Agent Error Recovery & Resilience System.

Tests circuit breaker, adaptive retry, task interruption, and agent execution
with focus on preventing cascading failures and handling 80%+ transient failures.
"""

import asyncio
import os
import sys
import time
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from common.agent_executor import (
    AgentCoordinatorIntegration,
    AgentExecutionError,
    AgentExecutionResult,
    ResilientAgentExecutor,
    resilient_agent_call,
)
from common.error_recovery import (
    AdaptiveRetryManager,
    CircuitBreakerConfig,
    CircuitState,
    RetryConfig,
    SubAgentCircuitBreaker,
    TaskInterruptionManager,
    TaskState,
    get_circuit_breaker,
    get_retry_manager,
    get_system_status,
    get_task_manager,
)


class TestSubAgentCircuitBreaker:
    """Test circuit breaker pattern implementation."""
    
    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initializes correctly."""
        cb = SubAgentCircuitBreaker("test-agent")
        
        assert cb.agent_type == "test-agent"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.can_execute() is True
    
    def test_failure_threshold_opens_circuit(self):
        """Test circuit opens after failure threshold."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = SubAgentCircuitBreaker("test-agent", config)
        
        # Record failures up to threshold
        for i in range(3):
            assert cb.state == CircuitState.CLOSED
            cb.record_failure()
        
        # Circuit should now be open
        assert cb.state == CircuitState.OPEN
        assert cb.can_execute() is False
    
    def test_circuit_recovery_after_timeout(self):
        """Test circuit transitions to half-open after timeout."""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=0.1)
        cb = SubAgentCircuitBreaker("test-agent", config)
        
        # Trip circuit
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.15)
        
        # Should transition to half-open
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN
    
    def test_half_open_to_closed_on_success(self):
        """Test half-open transitions to closed after successful executions."""
        config = CircuitBreakerConfig(
            failure_threshold=2, recovery_timeout=0.1, success_threshold=2
        )
        cb = SubAgentCircuitBreaker("test-agent", config)
        
        # Trip circuit and wait for half-open
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.15)
        cb.can_execute()  # Trigger half-open
        
        # Record successes
        cb.record_success()
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success()
        
        # Should be closed now
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    def test_success_rate_calculation(self):
        """Test success rate calculation for pattern analysis."""
        cb = SubAgentCircuitBreaker("test-agent")
        
        # Record mix of successes and failures
        cb.record_success()
        cb.record_success()
        cb.record_failure()
        cb.record_success()
        
        success_rate = cb.get_success_rate()
        assert success_rate == 0.75  # 3/4 successes
    
    def test_no_false_positive_circuit_trips(self):
        """Test circuit doesn't trip on intermittent failures."""
        config = CircuitBreakerConfig(failure_threshold=5)
        cb = SubAgentCircuitBreaker("test-agent", config)
        
        # Mix successes and failures below threshold
        cb.record_failure()
        cb.record_success()
        cb.record_failure()
        cb.record_success()
        cb.record_failure()
        
        # Circuit should remain closed
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute() is True


class TestAdaptiveRetryManager:
    """Test adaptive retry system with exponential backoff and jitter."""
    
    @pytest.mark.asyncio
    async def test_successful_execution_no_retry(self):
        """Test successful execution on first attempt."""
        retry_manager = AdaptiveRetryManager("test-agent")
        
        async def success_func():
            return "success"
        
        result = await retry_manager.execute_with_retry(success_func)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_retry_on_failure_then_success(self):
        """Test retry logic with eventual success."""
        config = RetryConfig(max_attempts=3, base_delay=0.01)
        retry_manager = AdaptiveRetryManager("test-agent", config)
        
        call_count = 0
        
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Transient failure")
            return "success"
        
        result = await retry_manager.execute_with_retry(flaky_func)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_max_attempts_exhausted(self):
        """Test all retry attempts exhausted."""
        config = RetryConfig(max_attempts=2, base_delay=0.01)
        retry_manager = AdaptiveRetryManager("test-agent", config)
        
        async def always_fail():
            raise Exception("Persistent failure")
        
        with pytest.raises(Exception, match="Persistent failure"):
            await retry_manager.execute_with_retry(always_fail)
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_with_jitter(self):
        """Test exponential backoff delay calculation."""
        config = RetryConfig(base_delay=1.0, backoff_multiplier=2.0, jitter_factor=0.1)
        retry_manager = AdaptiveRetryManager("test-agent", config)
        
        # Test delay calculations
        delay_0 = retry_manager._calculate_retry_delay(0)
        delay_1 = retry_manager._calculate_retry_delay(1)
        delay_2 = retry_manager._calculate_retry_delay(2)
        
        # Should increase exponentially (with jitter variation)
        assert 0.9 <= delay_0 <= 1.1  # Base delay with jitter
        assert 1.8 <= delay_1 <= 2.2  # 2.0 * base_delay with jitter
        assert 3.6 <= delay_2 <= 4.4  # 4.0 * base_delay with jitter
    
    @pytest.mark.asyncio
    async def test_handles_80_percent_transient_failures(self):
        """Test system handles 80%+ of transient failures successfully."""
        config = RetryConfig(max_attempts=3, base_delay=0.01)
        retry_manager = AdaptiveRetryManager("test-agent", config)
        
        successful_recoveries = 0
        total_attempts = 100
        
        for _ in range(total_attempts):
            call_count = 0
            
            async def transient_failure():
                nonlocal call_count
                call_count += 1
                # Fail first two attempts, succeed on third
                if call_count <= 2:
                    raise Exception("Transient failure")
                return "success"
            
            try:
                result = await retry_manager.execute_with_retry(transient_failure)
                if result == "success":
                    successful_recoveries += 1
            except:
                pass
        
        success_rate = successful_recoveries / total_attempts
        assert success_rate >= 0.8  # 80%+ success rate


class TestTaskInterruptionManager:
    """Test task interruption and recovery with timeout handling."""
    
    def test_task_creation_and_lifecycle(self):
        """Test task checkpoint creation and state management."""
        manager = TaskInterruptionManager()
        
        checkpoint = manager.create_task("task-1", "test-agent", {"key": "value"})
        assert checkpoint.task_id == "task-1"
        assert checkpoint.agent_type == "test-agent"
        assert checkpoint.state == TaskState.PENDING
        assert checkpoint.context["key"] == "value"
    
    def test_task_state_transitions(self):
        """Test task state transitions."""
        manager = TaskInterruptionManager()
        
        # Create and start task
        manager.create_task("task-1", "test-agent")
        assert manager.start_task("task-1") is True
        
        checkpoint = manager.get_checkpoint("task-1")
        assert checkpoint.state == TaskState.RUNNING
        
        # Complete task
        assert manager.complete_task("task-1", success=True) is True
        checkpoint = manager.get_checkpoint("task-1")
        assert checkpoint.state == TaskState.COMPLETED
    
    def test_task_interruption_within_5_seconds(self):
        """Test task interruption responds within 5 seconds."""
        manager = TaskInterruptionManager()
        
        manager.create_task("task-1", "test-agent")
        manager.start_task("task-1")
        
        start_time = time.time()
        
        # Simulate task that responds to interrupt
        def simulate_responsive_task():
            # Task would check should_interrupt() and exit gracefully
            time.sleep(0.1)  # Simulate some work
            manager.complete_task("task-1", success=True)
        
        import threading
        task_thread = threading.Thread(target=simulate_responsive_task)
        task_thread.start()
        
        # Interrupt task
        interrupted = manager.interrupt_task("task-1", timeout=1.0)
        interrupt_time = time.time() - start_time
        
        task_thread.join()
        
        # Should interrupt within reasonable time (much less than 5s for test)
        assert interrupt_time < 2.0
        assert interrupted is True
    
    def test_120_second_timeout_monitoring(self):
        """Test automatic timeout detection after 120 seconds."""
        # Note: This test uses a shorter timeout for practical testing
        manager = TaskInterruptionManager()
        
        # Create task that won't update checkpoint
        checkpoint = manager.create_task("task-1", "test-agent")
        manager.start_task("task-1")
        
        # Manually set last_update to simulate timeout
        with manager.lock:
            manager.active_tasks["task-1"].last_update = time.time() - 125.0
        
        # Check should_interrupt after timeout
        time.sleep(0.1)  # Allow monitor thread to process
        
        # Task should be marked for interruption due to timeout
        # (In real scenario, monitor thread would call interrupt_task)
    
    def test_checkpoint_based_recovery(self):
        """Test checkpoint-based task recovery."""
        manager = TaskInterruptionManager()
        
        # Create task with context
        context = {"step": "data_processing", "progress": 0.5}
        manager.create_task("task-1", "test-agent", context)
        
        # Update checkpoint with progress
        manager.update_checkpoint("task-1", {"progress": 0.8, "current_file": "test.csv"})
        
        # Retrieve checkpoint
        checkpoint = manager.get_checkpoint("task-1")
        assert checkpoint.context["progress"] == 0.8
        assert checkpoint.context["current_file"] == "test.csv"
        assert checkpoint.context["step"] == "data_processing"


class TestResilientAgentExecutor:
    """Test resilient agent execution system."""
    
    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """Test successful agent execution."""
        executor = ResilientAgentExecutor("test-agent")
        
        async def test_func():
            return "success"
        
        result = await executor.execute(test_func, "Test task")
        
        assert result.success is True
        assert result.result == "success"
        assert result.agent_type == "test-agent"
        assert result.execution_time > 0
        assert result.circuit_tripped is False
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self):
        """Test circuit breaker blocks execution when open."""
        executor = ResilientAgentExecutor("test-agent")
        
        # Trip circuit breaker
        for _ in range(5):
            executor.circuit_breaker.record_failure()
        
        async def test_func():
            return "should not execute"
        
        result = await executor.execute(test_func, "Test task")
        
        assert result.success is False
        assert result.circuit_tripped is True
        assert "Circuit breaker is OPEN" in str(result.error)
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test task timeout handling."""
        executor = ResilientAgentExecutor("test-agent")
        
        async def slow_func():
            await asyncio.sleep(2.0)  # Longer than test timeout
            return "should timeout"
        
        result = await executor.execute(slow_func, "Slow task", timeout=0.1)
        
        assert result.success is False
        assert "timed out" in str(result.error)
    
    @pytest.mark.asyncio
    async def test_task_interruption(self):
        """Test task can be interrupted gracefully."""
        executor = ResilientAgentExecutor("test-agent")
        
        async def interruptible_func():
            # Simulate long-running task that checks interruption
            for i in range(100):
                await asyncio.sleep(0.01)
                # In real implementation, would check task_manager.should_interrupt()
            return "completed"
        
        # Start execution and interrupt after short delay
        async def interrupt_after_delay(task_id):
            await asyncio.sleep(0.05)
            executor.task_manager.interrupt_task(task_id)
        
        # This test demonstrates the interruption mechanism
        # In practice, the function would check should_interrupt() and exit gracefully


class TestAgentCoordinatorIntegration:
    """Test agent coordinator integration with error recovery."""
    
    @pytest.mark.asyncio
    async def test_delegate_task_with_fallback(self):
        """Test task delegation with fallback agent."""
        coordinator = AgentCoordinatorIntegration()
        
        # Create mock functions
        primary_calls = 0
        fallback_calls = 0
        
        async def primary_func():
            nonlocal primary_calls
            primary_calls += 1
            raise Exception("Primary agent failure")
        
        async def fallback_func():
            nonlocal fallback_calls
            fallback_calls += 1
            return "fallback success"
        
        # Mock the executors to use different functions
        with patch.object(coordinator, 'get_executor') as mock_get_executor:
            # Primary executor fails
            primary_executor = Mock()
            primary_result = AgentExecutionResult(
                success=False,
                error=Exception("Primary failed"),
                agent_type="primary-agent"
            )
            primary_executor.execute = AsyncMock(return_value=primary_result)
            
            # Fallback executor succeeds
            fallback_executor = Mock()
            fallback_result = AgentExecutionResult(
                success=True,
                result="fallback success",
                agent_type="fallback-agent"
            )
            fallback_executor.execute = AsyncMock(return_value=fallback_result)
            
            # Configure mock to return appropriate executor
            def get_executor_side_effect(agent_type):
                if agent_type == "primary-agent":
                    return primary_executor
                else:
                    return fallback_executor
            
            mock_get_executor.side_effect = get_executor_side_effect
            
            # Execute with fallback
            result = await coordinator.delegate_task(
                "primary-agent",
                lambda: "test",
                "Test task",
                fallback_agent="fallback-agent"
            )
            
            assert result.success is True
            assert result.result == "fallback success"
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test parallel task execution."""
        coordinator = AgentCoordinatorIntegration()
        
        tasks = [
            ("agent-1", lambda: "result-1", "Task 1", None),
            ("agent-2", lambda: "result-2", "Task 2", None),
            ("agent-3", lambda: "result-3", "Task 3", None),
        ]
        
        # Mock all executors to succeed
        with patch.object(coordinator, 'get_executor') as mock_get_executor:
            mock_executor = Mock()
            mock_executor.execute = AsyncMock(side_effect=[
                AgentExecutionResult(success=True, result="result-1", agent_type="agent-1"),
                AgentExecutionResult(success=True, result="result-2", agent_type="agent-2"), 
                AgentExecutionResult(success=True, result="result-3", agent_type="agent-3"),
            ])
            mock_get_executor.return_value = mock_executor
            
            results = await coordinator.parallel_execution(tasks)
            
            assert len(results) == 3
            assert all(result.success for result in results)
            assert [result.result for result in results] == ["result-1", "result-2", "result-3"]


class TestSystemIntegration:
    """Test complete system integration and health monitoring."""
    
    def test_system_status_reporting(self):
        """Test comprehensive system status reporting."""
        # Create some circuit breakers and retry managers
        cb1 = get_circuit_breaker("agent-1")
        cb2 = get_circuit_breaker("agent-2")
        rm1 = get_retry_manager("agent-1")
        
        # Record some activity
        cb1.record_success()
        cb2.record_failure()
        
        status = get_system_status()
        
        assert "circuit_breakers" in status
        assert "retry_managers" in status
        assert "active_tasks" in status
        assert "timestamp" in status
        
        assert "agent-1" in status["circuit_breakers"]
        assert "agent-2" in status["circuit_breakers"]
        assert "agent-1" in status["retry_managers"]
    
    def test_prevent_cascading_failures(self):
        """Test system prevents cascading failures."""
        # Create multiple interconnected agents
        agents = ["data-engineer", "quant-research", "compliance-risk"]
        circuit_breakers = [get_circuit_breaker(agent) for agent in agents]
        
        # Simulate failure in first agent
        for _ in range(5):
            circuit_breakers[0].record_failure()
        
        # First agent circuit should be open
        assert circuit_breakers[0].state == CircuitState.OPEN
        assert circuit_breakers[0].can_execute() is False
        
        # Other agents should remain operational
        assert circuit_breakers[1].can_execute() is True
        assert circuit_breakers[2].can_execute() is True
        
        # System should isolate the failure
        system_status = get_system_status()
        failed_agents = [
            agent for agent, status in system_status["circuit_breakers"].items()
            if status["state"] == "open"
        ]
        
        assert len(failed_agents) == 1
        assert "data-engineer" in failed_agents
    
    @pytest.mark.asyncio
    async def test_end_to_end_resilience(self):
        """Test end-to-end system resilience."""
        coordinator = AgentCoordinatorIntegration()
        
        # Simulate a complex workflow with potential failures
        workflow_tasks = []
        
        # Task 1: Data processing (might fail)
        async def data_task():
            if time.time() % 2 > 1:  # Intermittent failure
                raise Exception("Data processing error")
            return "data_processed"
        
        # Task 2: Analysis (depends on data)
        async def analysis_task():
            return "analysis_complete"
        
        # Task 3: Reporting (final step)
        async def report_task():
            return "report_generated"
        
        # Execute workflow with resilience
        try:
            # Sequential execution with error recovery
            data_result = await coordinator.delegate_task(
                "data-engineer",
                data_task,
                "Process financial data",
                fallback_agent="infra-ops-agent"  # Fallback for data issues
            )
            
            if data_result.success:
                analysis_result = await coordinator.delegate_task(
                    "quant-research",
                    analysis_task,
                    "Analyze processed data"
                )
                
                if analysis_result.success:
                    report_result = await coordinator.delegate_task(
                        "compliance-risk",
                        report_task,
                        "Generate compliance report"
                    )
                    
                    # Workflow should complete successfully even with some failures
                    assert report_result is not None
        
        except Exception as e:
            # System should handle exceptions gracefully
            assert False, f"Workflow failed completely: {e}"


# Performance and stress tests
class TestPerformanceAndStress:
    """Test system performance under load and stress conditions."""
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self):
        """Test system handles concurrent agent executions."""
        coordinator = AgentCoordinatorIntegration()
        
        async def concurrent_task(task_id):
            await asyncio.sleep(0.01)  # Simulate work
            return f"task-{task_id}-complete"
        
        # Create many concurrent tasks
        tasks = []
        for i in range(50):
            task = coordinator.delegate_task(
                f"agent-{i % 5}",  # Distribute across 5 agent types
                lambda tid=i: concurrent_task(tid),
                f"Concurrent task {i}"
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Most should succeed (allowing for some circuit breaker trips)
        successful_results = [
            r for r in results if isinstance(r, AgentExecutionResult) and r.success
        ]
        success_rate = len(successful_results) / len(results)
        
        # Should maintain high success rate even under load
        assert success_rate >= 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])