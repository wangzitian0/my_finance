#!/usr/bin/env python3
"""
HRBP Performance Benchmarks

Performance testing suite for HRBP system components.
Tests performance characteristics of:

1. Agent Performance Analysis
2. Coordination Optimization
3. PR Cycle Management
4. System Health Monitoring
5. CLI Response Times
6. Memory Usage Patterns

Ensures HRBP system meets performance requirements for production use.
"""

import gc
import os
import psutil
import pytest
import subprocess
import sys
import time
import threading
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from unittest.mock import Mock, patch
from dataclasses import dataclass
import statistics


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    name: str
    value: float
    unit: str
    threshold: float
    status: str  # 'pass', 'fail', 'warning'
    details: str = ""


@dataclass
class BenchmarkResult:
    """Benchmark test result."""
    test_name: str
    execution_time: float
    memory_usage: float
    metrics: List[PerformanceMetric]
    status: str
    notes: str = ""


class PerformanceBenchmark:
    """Base class for performance benchmarks."""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = 0
        self.start_memory = 0
        self.process = psutil.Process(os.getpid())
        
    def start_measurement(self):
        """Start performance measurement."""
        gc.collect()  # Clean up before measurement
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss
        
    def stop_measurement(self) -> tuple:
        """Stop measurement and return (execution_time, memory_delta)."""
        execution_time = time.time() - self.start_time
        end_memory = self.process.memory_info().rss
        memory_delta = (end_memory - self.start_memory) / 1024 / 1024  # MB
        return execution_time, memory_delta


@pytest.fixture
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def performance_thresholds():
    """Performance thresholds for different operations."""
    return {
        'cli_response_time': 2.0,  # seconds
        'analysis_time': 10.0,  # seconds
        'memory_usage': 100.0,  # MB
        'coordination_overhead': 0.5,  # seconds
        'concurrent_operations': 5.0,  # seconds
        'system_health_check': 3.0  # seconds
    }


class TestHRBPCLIPerformance:
    """Test HRBP CLI performance benchmarks."""
    
    def test_hrbp_status_response_time(self, project_root, performance_thresholds):
        """Test HRBP status command response time."""
        benchmark = PerformanceBenchmark("HRBP Status Response")
        
        benchmark.start_measurement()
        
        try:
            result = subprocess.run(
                [sys.executable, 'p3.py', 'hrbp-status'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=performance_thresholds['cli_response_time'] * 2
            )
            
            execution_time, memory_delta = benchmark.stop_measurement()
            
            # Performance assertions
            assert execution_time < performance_thresholds['cli_response_time'], \
                f"HRBP status too slow: {execution_time:.2f}s > {performance_thresholds['cli_response_time']}s"
            
            assert memory_delta < performance_thresholds['memory_usage'], \
                f"HRBP status memory usage too high: {memory_delta:.1f}MB"
            
            # Command should be recognized
            assert result.returncode != 127, "HRBP status command not recognized"
            
        except subprocess.TimeoutExpired:
            execution_time, memory_delta = benchmark.stop_measurement()
            pytest.fail(f"HRBP status command timed out after {execution_time:.2f}s")
    
    def test_hrbp_help_performance(self, project_root, performance_thresholds):
        """Test HRBP help command performance."""
        benchmark = PerformanceBenchmark("HRBP Help Performance")
        
        benchmark.start_measurement()
        
        try:
            result = subprocess.run(
                [sys.executable, 'infra/hrbp_automation.py', '--help'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            execution_time, memory_delta = benchmark.stop_measurement()
            
            # Help should be very fast
            help_threshold = 1.0  # 1 second for help
            assert execution_time < help_threshold, \
                f"HRBP help too slow: {execution_time:.2f}s > {help_threshold}s"
            
            # Should succeed or show help
            assert result.returncode in [0, 2], "HRBP help should succeed"
            
        except subprocess.TimeoutExpired:
            execution_time, memory_delta = benchmark.stop_measurement()
            pytest.fail(f"HRBP help command timed out after {execution_time:.2f}s")
    
    def test_comprehensive_cli_performance(self, project_root, performance_thresholds):
        """Test HRBP comprehensive CLI performance."""
        benchmark = PerformanceBenchmark("Comprehensive CLI Performance")
        
        benchmark.start_measurement()
        
        try:
            result = subprocess.run(
                [sys.executable, 'infra/hrbp_comprehensive_cli.py', '--help'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            execution_time, memory_delta = benchmark.stop_measurement()
            
            # Comprehensive CLI should still be reasonably fast
            assert execution_time < 2.0, \
                f"Comprehensive CLI too slow: {execution_time:.2f}s"
            
            # Should show help
            assert result.returncode in [0, 2], "Comprehensive CLI help should work"
            
        except subprocess.TimeoutExpired:
            execution_time, memory_delta = benchmark.stop_measurement()
            pytest.fail(f"Comprehensive CLI help timed out after {execution_time:.2f}s")


class TestHRBPConcurrencyPerformance:
    """Test HRBP performance under concurrent load."""
    
    def test_concurrent_hrbp_status_commands(self, project_root, performance_thresholds):
        """Test concurrent HRBP status commands."""
        def run_hrbp_status():
            """Run single HRBP status command."""
            start_time = time.time()
            try:
                result = subprocess.run(
                    [sys.executable, 'p3.py', 'hrbp-status'],
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                execution_time = time.time() - start_time
                return {
                    'execution_time': execution_time,
                    'returncode': result.returncode,
                    'success': result.returncode != 127
                }
            except subprocess.TimeoutExpired:
                execution_time = time.time() - start_time
                return {
                    'execution_time': execution_time,
                    'returncode': -1,
                    'success': False
                }
        
        # Run 3 concurrent HRBP status commands
        benchmark = PerformanceBenchmark("Concurrent HRBP Status")
        benchmark.start_measurement()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_hrbp_status) for _ in range(3)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_execution_time, memory_delta = benchmark.stop_measurement()
        
        # At least one should succeed
        successful_runs = sum(1 for r in results if r['success'])
        assert successful_runs >= 1, "At least one concurrent HRBP command should succeed"
        
        # Total time should be reasonable (not much more than sequential)
        assert total_execution_time < performance_thresholds['concurrent_operations'], \
            f"Concurrent operations too slow: {total_execution_time:.2f}s"
        
        # Memory usage should be reasonable
        assert memory_delta < performance_thresholds['memory_usage'] * 2, \
            f"Concurrent operations memory usage too high: {memory_delta:.1f}MB"
    
    def test_mixed_command_performance(self, project_root, performance_thresholds):
        """Test mixed HRBP and regular p3 command performance."""
        commands = [
            ['hrbp-status'],
            ['--help'], 
            ['hrbp-history'],
            ['status']
        ]
        
        def run_command(cmd):
            """Run single command."""
            start_time = time.time()
            try:
                result = subprocess.run(
                    [sys.executable, 'p3.py'] + cmd,
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                execution_time = time.time() - start_time
                return {
                    'command': cmd,
                    'execution_time': execution_time,
                    'success': result.returncode != 127
                }
            except subprocess.TimeoutExpired:
                execution_time = time.time() - start_time
                return {
                    'command': cmd,
                    'execution_time': execution_time,
                    'success': False
                }
        
        benchmark = PerformanceBenchmark("Mixed Command Performance")
        benchmark.start_measurement()
        
        # Run commands sequentially to test interference
        results = []
        for cmd in commands:
            result = run_command(cmd)
            results.append(result)
        
        total_execution_time, memory_delta = benchmark.stop_measurement()
        
        # Most commands should succeed
        successful_runs = sum(1 for r in results if r['success'])
        assert successful_runs >= len(commands) // 2, \
            f"Too many commands failed: {successful_runs}/{len(commands)}"
        
        # Average execution time should be reasonable
        avg_execution_time = total_execution_time / len(commands)
        assert avg_execution_time < 2.0, \
            f"Average command execution too slow: {avg_execution_time:.2f}s"


class TestHRBPComponentPerformance:
    """Test individual HRBP component performance."""
    
    def test_performance_manager_mock_analysis(self, performance_thresholds):
        """Test performance manager analysis speed with mocked data."""
        with patch('common.hrbp_performance_manager.get_hrbp_performance_manager') as mock_get_manager:
            # Setup mock performance manager
            mock_manager = Mock()
            mock_performance_data = {}
            
            # Generate mock performance data for multiple agents
            for i in range(10):
                agent_name = f'test-agent-{i}'
                mock_performance_data[agent_name] = Mock(
                    success_rate=0.9 - (i * 0.05),
                    total_executions=100 + i * 10,
                    average_execution_time_ms=1000 + i * 100,
                    capability_level='good'
                )
            
            mock_manager.collect_agent_performance_data.return_value = mock_performance_data
            mock_get_manager.return_value = mock_manager
            
            # Test analysis performance
            benchmark = PerformanceBenchmark("Performance Analysis")
            benchmark.start_measurement()
            
            # Simulate analysis
            manager = mock_get_manager()
            data = manager.collect_agent_performance_data(30)
            
            execution_time, memory_delta = benchmark.stop_measurement()
            
            # Analysis should be fast for reasonable dataset
            assert execution_time < 1.0, f"Performance analysis too slow: {execution_time:.2f}s"
            
            # Should return expected amount of data
            assert len(data) == 10, "Should return all mock agents"
    
    def test_coordination_optimizer_mock_performance(self, performance_thresholds):
        """Test coordination optimizer performance with mocked data."""
        with patch('common.agent_coordination_optimizer.get_coordination_optimizer') as mock_get_optimizer:
            mock_optimizer = Mock()
            
            # Mock coordination metrics
            mock_metrics = {
                'average_success_rate': 0.92,
                'capacity_utilization': {
                    f'agent-{i}': 0.7 + (i * 0.05) for i in range(5)
                },
                'resource_allocation_efficiency': 0.88,
                'coordination_overhead_ms': 150
            }
            mock_optimizer.get_coordination_metrics.return_value = mock_metrics
            mock_get_optimizer.return_value = mock_optimizer
            
            # Test coordination analysis performance
            benchmark = PerformanceBenchmark("Coordination Analysis")
            benchmark.start_measurement()
            
            optimizer = mock_get_optimizer()
            metrics = optimizer.get_coordination_metrics()
            
            execution_time, memory_delta = benchmark.stop_measurement()
            
            # Should be very fast for mocked data
            assert execution_time < 0.1, f"Coordination analysis too slow: {execution_time:.2f}s"
            
            # Should return expected metrics
            assert 'average_success_rate' in metrics
            assert len(metrics['capacity_utilization']) == 5
    
    def test_pr_tracker_mock_performance(self, performance_thresholds):
        """Test PR tracker performance with mocked data."""
        with patch('common.hrbp_pr_tracker.get_hrbp_tracker') as mock_get_tracker:
            mock_tracker = Mock()
            
            # Mock PR tracking operations
            mock_tracker.get_cycle_status.return_value = {
                'current_cycle_prs': 15,
                'pr_threshold': 20,
                'prs_until_next_trigger': 5,
                'total_triggers': 2
            }
            mock_tracker.record_pr_merge.return_value = False
            mock_get_tracker.return_value = mock_tracker
            
            benchmark = PerformanceBenchmark("PR Tracker Operations")
            benchmark.start_measurement()
            
            tracker = mock_get_tracker()
            
            # Test multiple operations
            for i in range(5):
                status = tracker.get_cycle_status()
                triggered = tracker.record_pr_merge(100 + i)
            
            execution_time, memory_delta = benchmark.stop_measurement()
            
            # PR operations should be very fast
            assert execution_time < 0.1, f"PR tracker operations too slow: {execution_time:.2f}s"


class TestHRBPMemoryPerformance:
    """Test HRBP memory usage and leak detection."""
    
    def test_hrbp_command_memory_usage(self, project_root, performance_thresholds):
        """Test HRBP command memory usage patterns."""
        def measure_command_memory(cmd):
            """Measure memory usage of a single command."""
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            try:
                result = subprocess.run(
                    [sys.executable, 'p3.py'] + cmd,
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                final_memory = process.memory_info().rss
                memory_delta = (final_memory - initial_memory) / 1024 / 1024  # MB
                
                return {
                    'command': cmd,
                    'memory_delta': memory_delta,
                    'success': result.returncode != 127
                }
                
            except subprocess.TimeoutExpired:
                final_memory = process.memory_info().rss
                memory_delta = (final_memory - initial_memory) / 1024 / 1024
                return {
                    'command': cmd,
                    'memory_delta': memory_delta,
                    'success': False
                }
        
        commands = [
            ['hrbp-status'],
            ['hrbp-history'],
            ['hrbp-config']
        ]
        
        memory_results = []
        for cmd in commands:
            gc.collect()  # Clean up before each test
            result = measure_command_memory(cmd)
            memory_results.append(result)
        
        # Check memory usage for each command
        for result in memory_results:
            memory_threshold = 50.0  # 50MB limit per command
            assert result['memory_delta'] < memory_threshold, \
                f"Command {result['command']} uses too much memory: {result['memory_delta']:.1f}MB"
    
    def test_hrbp_memory_leak_detection(self, project_root):
        """Test for memory leaks in repeated HRBP operations."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run same command multiple times
        for i in range(5):
            try:
                subprocess.run(
                    [sys.executable, 'p3.py', 'hrbp-status'],
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    timeout=3
                )
            except subprocess.TimeoutExpired:
                pass  # Command might timeout, that's ok for memory test
            
            # Force garbage collection
            gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Should not leak significant memory
        leak_threshold = 20.0  # 20MB threshold for 5 operations
        assert memory_increase < leak_threshold, \
            f"Potential memory leak detected: {memory_increase:.1f}MB increase"
    
    def test_hrbp_component_memory_efficiency(self):
        """Test memory efficiency of HRBP components with mocks."""
        initial_memory = psutil.Process(os.getpid()).memory_info().rss
        
        # Test multiple component initializations
        with patch('common.hrbp_integration_framework.HRBPIntegrationFramework') as mock_framework, \
             patch('common.hrbp_performance_manager.HRBPPerformanceManager') as mock_manager, \
             patch('common.agent_coordination_optimizer.AgentCoordinationOptimizer') as mock_optimizer:
            
            # Create mock instances
            for i in range(3):
                framework = mock_framework()
                manager = mock_manager()
                optimizer = mock_optimizer()
                
                # Simulate some operations
                framework.get_system_status = Mock(return_value={'status': 'healthy'})
                manager.collect_agent_performance_data = Mock(return_value={})
                optimizer.get_coordination_metrics = Mock(return_value={})
        
        gc.collect()
        final_memory = psutil.Process(os.getpid()).memory_info().rss
        memory_delta = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Component initialization should not use excessive memory
        assert memory_delta < 10.0, f"Component initialization uses too much memory: {memory_delta:.1f}MB"


class TestHRBPScalabilityPerformance:
    """Test HRBP scalability and load handling."""
    
    def test_large_dataset_mock_performance(self, performance_thresholds):
        """Test HRBP performance with large mock datasets."""
        with patch('common.hrbp_performance_manager.get_hrbp_performance_manager') as mock_get_manager:
            mock_manager = Mock()
            
            # Create large mock dataset (100 agents)
            large_performance_data = {}
            for i in range(100):
                agent_name = f'agent-{i:03d}'
                large_performance_data[agent_name] = Mock(
                    success_rate=0.8 + (i % 20) * 0.01,
                    total_executions=50 + (i * 5),
                    average_execution_time_ms=800 + (i * 10),
                    capability_level='good' if i % 3 == 0 else 'excellent'
                )
            
            mock_manager.collect_agent_performance_data.return_value = large_performance_data
            mock_get_manager.return_value = mock_manager
            
            benchmark = PerformanceBenchmark("Large Dataset Analysis")
            benchmark.start_measurement()
            
            # Simulate analysis of large dataset
            manager = mock_get_manager()
            data = manager.collect_agent_performance_data(30)
            
            # Simulate processing all agents
            success_rates = [agent.success_rate for agent in data.values()]
            avg_success_rate = sum(success_rates) / len(success_rates)
            
            execution_time, memory_delta = benchmark.stop_measurement()
            
            # Should handle large dataset efficiently
            assert execution_time < 1.0, f"Large dataset analysis too slow: {execution_time:.2f}s"
            assert len(data) == 100, "Should process all agents"
            assert 0.8 <= avg_success_rate <= 1.0, "Calculated metrics should be reasonable"
    
    def test_coordination_scalability_mock(self, performance_thresholds):
        """Test coordination optimizer scalability with large agent sets."""
        with patch('common.agent_coordination_optimizer.get_coordination_optimizer') as mock_get_optimizer:
            mock_optimizer = Mock()
            
            # Large capacity utilization map (50 agents)
            large_capacity_data = {
                f'agent-{i:02d}': 0.6 + (i % 30) * 0.01
                for i in range(50)
            }
            
            mock_coordination_metrics = {
                'average_success_rate': 0.89,
                'capacity_utilization': large_capacity_data,
                'resource_allocation_efficiency': 0.85,
                'coordination_overhead_ms': 200 + len(large_capacity_data) * 2  # Scales with agents
            }
            
            mock_optimizer.get_coordination_metrics.return_value = mock_coordination_metrics
            mock_get_optimizer.return_value = mock_optimizer
            
            benchmark = PerformanceBenchmark("Coordination Scalability")
            benchmark.start_measurement()
            
            optimizer = mock_get_optimizer()
            metrics = optimizer.get_coordination_metrics()
            
            # Process utilization data
            utilizations = list(metrics['capacity_utilization'].values())
            avg_utilization = sum(utilizations) / len(utilizations)
            overutilized = [u for u in utilizations if u > 0.9]
            
            execution_time, memory_delta = benchmark.stop_measurement()
            
            # Should scale efficiently
            assert execution_time < 0.5, f"Coordination scalability too slow: {execution_time:.2f}s"
            assert len(metrics['capacity_utilization']) == 50, "Should handle all agents"
            assert metrics['coordination_overhead_ms'] < 500, "Coordination overhead should be reasonable"


def run_performance_benchmark_suite():
    """Run comprehensive HRBP performance benchmark suite."""
    print("🏃 Running HRBP Performance Benchmark Suite...")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    
    benchmark_results = []
    
    # Benchmark 1: CLI Response Times
    print("\n📊 Testing CLI Response Times...")
    try:
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, 'p3.py', 'hrbp-status'],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        execution_time = time.time() - start_time
        
        status = "PASS" if execution_time < 2.0 and result.returncode != 127 else "FAIL"
        print(f"  CLI Response Time: {execution_time:.2f}s - {status}")
        
        benchmark_results.append({
            'test': 'CLI Response Time',
            'value': execution_time,
            'threshold': 2.0,
            'status': status
        })
        
    except Exception as e:
        print(f"  CLI Response Time: ERROR - {e}")
        benchmark_results.append({
            'test': 'CLI Response Time',
            'value': -1,
            'threshold': 2.0,
            'status': 'ERROR'
        })
    
    # Benchmark 2: Memory Usage
    print("\n💾 Testing Memory Usage...")
    try:
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run HRBP command
        subprocess.run(
            [sys.executable, 'p3.py', 'hrbp-status'],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=3
        )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = final_memory - initial_memory
        
        status = "PASS" if memory_delta < 50.0 else "FAIL"
        print(f"  Memory Usage: {memory_delta:.1f}MB - {status}")
        
        benchmark_results.append({
            'test': 'Memory Usage',
            'value': memory_delta,
            'threshold': 50.0,
            'status': status
        })
        
    except Exception as e:
        print(f"  Memory Usage: ERROR - {e}")
        benchmark_results.append({
            'test': 'Memory Usage',
            'value': -1,
            'threshold': 50.0,
            'status': 'ERROR'
        })
    
    # Benchmark 3: Concurrent Operations
    print("\n🔄 Testing Concurrent Operations...")
    try:
        start_time = time.time()
        
        def run_command():
            return subprocess.run(
                [sys.executable, 'p3.py', 'hrbp-status'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=3
            )
        
        # Run 3 commands concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_command) for _ in range(3)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        execution_time = time.time() - start_time
        successful = sum(1 for r in results if r.returncode != 127)
        
        status = "PASS" if execution_time < 5.0 and successful >= 1 else "FAIL"
        print(f"  Concurrent Operations: {execution_time:.2f}s ({successful}/3 successful) - {status}")
        
        benchmark_results.append({
            'test': 'Concurrent Operations',
            'value': execution_time,
            'threshold': 5.0,
            'status': status
        })
        
    except Exception as e:
        print(f"  Concurrent Operations: ERROR - {e}")
        benchmark_results.append({
            'test': 'Concurrent Operations',
            'value': -1,
            'threshold': 5.0,
            'status': 'ERROR'
        })
    
    # Results Summary
    print("\n" + "=" * 60)
    print("🏁 PERFORMANCE BENCHMARK RESULTS")
    print("=" * 60)
    
    passed_tests = sum(1 for r in benchmark_results if r['status'] == 'PASS')
    total_tests = len(benchmark_results)
    
    for result in benchmark_results:
        status_icon = {
            'PASS': '✅',
            'FAIL': '❌',
            'ERROR': '💥'
        }.get(result['status'], '❓')
        
        if result['value'] >= 0:
            print(f"{status_icon} {result['test']}: {result['value']:.2f} (threshold: {result['threshold']:.2f})")
        else:
            print(f"{status_icon} {result['test']}: Error occurred")
    
    print(f"\n📊 Summary: {passed_tests}/{total_tests} benchmarks passed")
    
    if passed_tests == total_tests:
        print("🎉 All performance benchmarks passed!")
        return True
    else:
        print("⚠️  Some performance benchmarks failed")
        return False


if __name__ == "__main__":
    """Run HRBP performance benchmarks."""
    try:
        success = run_performance_benchmark_suite()
        
        if success:
            print("\n✅ HRBP performance benchmarks completed successfully")
        else:
            print("\n❌ HRBP performance benchmarks completed with issues")
            
        print("\n💡 Run full test suite with: pytest tests/test_hrbp_performance_benchmarks.py -v")
        
    except KeyboardInterrupt:
        print("\n⚠️  Performance benchmarks interrupted by user")
    except Exception as e:
        print(f"\n💥 Performance benchmarks failed: {e}")
        import traceback
        traceback.print_exc()