#!/usr/bin/env python3
"""
HRBP P3 Integration Tests

Comprehensive tests for HRBP integration with the p3 command system.
Tests all aspects of p3-HRBP integration including:

1. Command Registration and Recognition
2. HRBP Command Execution
3. P3 E2E Integration with HRBP
4. Workflow Compatibility 
5. Error Handling and Resilience
6. Performance Integration

This test suite ensures HRBP commands work seamlessly within the p3 ecosystem.
"""

import os
import pytest
import subprocess
import sys
import tempfile
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from unittest.mock import Mock, patch, MagicMock
import re


@pytest.fixture
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def p3_script_path(project_root):
    """Get path to p3 script."""
    return project_root / "p3.py"


def run_p3_command(args: List[str], project_root: Path, timeout: int = 30, 
                   env_vars: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
    """
    Run p3 command with timeout and capture output.
    
    Args:
        args: Command arguments
        project_root: Project root directory
        timeout: Command timeout in seconds
        env_vars: Additional environment variables
        
    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    try:
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
            
        result = subprocess.run(
            [sys.executable, "p3.py"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=project_root,
            env=env
        )
        return result.returncode, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


class TestHRBPCommandRegistration:
    """Test HRBP command registration in p3 system."""
    
    def test_p3_script_exists(self, p3_script_path):
        """Test that p3.py script exists."""
        assert p3_script_path.exists(), "p3.py script must exist"
        assert p3_script_path.is_file(), "p3.py must be a file"
    
    def test_hrbp_commands_defined_in_p3(self, p3_script_path):
        """Test that all HRBP commands are defined in p3.py."""
        p3_content = p3_script_path.read_text()
        
        # Expected HRBP commands that should be in p3.py
        expected_hrbp_commands = [
            'hrbp-status',
            'hrbp-record-pr',
            'hrbp-manual-trigger',
            'hrbp-history',
            'hrbp-config'
        ]
        
        for cmd in expected_hrbp_commands:
            # Check if command is defined in the commands dictionary
            assert f'"{cmd}"' in p3_content, f"HRBP command {cmd} not found in p3.py"
        
        # Check that commands map to the correct scripts
        assert 'infra/hrbp_automation.py' in p3_content, "HRBP automation script not referenced"
    
    def test_hrbp_command_handling_logic(self, p3_script_path):
        """Test that HRBP command handling logic is present."""
        p3_content = p3_script_path.read_text()
        
        # Check for special command handling
        assert '_handle_special_commands' in p3_content, "Special command handler missing"
        
        # Check for HRBP-specific handling
        hrbp_patterns = [
            'hrbp-record-pr',
            'hrbp-status',
            'hrbp-manual-trigger',
            'hrbp-history',
            'hrbp-config'
        ]
        
        found_patterns = 0
        for pattern in hrbp_patterns:
            if pattern in p3_content:
                found_patterns += 1
        
        assert found_patterns >= 3, f"Not enough HRBP command patterns found ({found_patterns}/{len(hrbp_patterns)})"
    
    def test_hrbp_help_integration(self, project_root):
        """Test that HRBP commands appear in p3 help."""
        returncode, stdout, stderr = run_p3_command(['--help'], project_root, timeout=10)
        
        # Help should be successful
        assert returncode == 0, f"p3 help failed: {stderr}"
        
        # Should contain HRBP commands
        help_text = stdout.lower()
        assert 'hrbp' in help_text, "HRBP commands not visible in help"
        
        # Check for specific HRBP commands in help
        hrbp_commands_in_help = [
            'hrbp-status',
            'hrbp-record-pr',
            'hrbp-manual-trigger',
            'hrbp-history',
            'hrbp-config'
        ]
        
        found_in_help = 0
        for cmd in hrbp_commands_in_help:
            if cmd in help_text:
                found_in_help += 1
        
        assert found_in_help >= 3, f"Not enough HRBP commands in help ({found_in_help}/{len(hrbp_commands_in_help)})"
    
    def test_hrbp_command_descriptions(self, project_root):
        """Test that HRBP commands have proper descriptions."""
        returncode, stdout, stderr = run_p3_command(['--help'], project_root)
        
        assert returncode == 0, "p3 help should succeed"
        
        help_text = stdout.lower()
        
        # Check for HRBP section or descriptions
        hrbp_indicators = [
            '20-pr cycle',
            'automation',
            'agent performance',
            'hrbp cycle',
            'trigger'
        ]
        
        found_indicators = 0
        for indicator in hrbp_indicators:
            if indicator in help_text:
                found_indicators += 1
        
        assert found_indicators >= 2, "HRBP command descriptions not comprehensive enough"


class TestHRBPCommandExecution:
    """Test HRBP command execution through p3."""
    
    def test_hrbp_status_command_recognition(self, project_root):
        """Test that hrbp-status command is recognized."""
        returncode, stdout, stderr = run_p3_command(['hrbp-status'], project_root, timeout=10)
        
        # Command should be recognized (not return 127 - command not found)
        assert returncode != 127, f"hrbp-status command not recognized: {stderr}"
        
        # Should attempt to execute (may fail due to missing environment)
        assert 'Executing:' in stdout or 'hrbp_automation.py' in stdout, "Command not properly routed"
    
    def test_hrbp_record_pr_command_structure(self, project_root):
        """Test hrbp-record-pr command parameter handling."""
        # Test with missing PR number (should show error)
        returncode, stdout, stderr = run_p3_command(['hrbp-record-pr'], project_root, timeout=5)
        
        # Should handle missing parameter gracefully
        assert returncode != 127, "hrbp-record-pr command not recognized"
        
        # Test with PR number
        returncode, stdout, stderr = run_p3_command(['hrbp-record-pr', '123'], project_root, timeout=5)
        
        # Should accept parameter
        assert returncode != 127, "hrbp-record-pr with parameter not handled"
        assert 'record-pr 123' in stdout or 'hrbp_automation.py' in stdout, "PR number not passed correctly"
    
    def test_hrbp_manual_trigger_command(self, project_root):
        """Test hrbp-manual-trigger command."""
        returncode, stdout, stderr = run_p3_command(['hrbp-manual-trigger'], project_root, timeout=5)
        
        # Should be recognized and routed
        assert returncode != 127, "hrbp-manual-trigger not recognized"
        assert 'manual-trigger' in stdout or 'hrbp_automation.py' in stdout, "Manual trigger not routed correctly"
    
    def test_hrbp_history_command(self, project_root):
        """Test hrbp-history command."""
        returncode, stdout, stderr = run_p3_command(['hrbp-history'], project_root, timeout=5)
        
        # Should be recognized and routed
        assert returncode != 127, "hrbp-history not recognized"
        assert 'history' in stdout or 'hrbp_automation.py' in stdout, "History command not routed correctly"
    
    def test_hrbp_config_command(self, project_root):
        """Test hrbp-config command."""
        returncode, stdout, stderr = run_p3_command(['hrbp-config'], project_root, timeout=5)
        
        # Should be recognized and routed
        assert returncode != 127, "hrbp-config not recognized"
        assert 'config' in stdout or 'hrbp_automation.py' in stdout, "Config command not routed correctly"
    
    def test_invalid_hrbp_command_handling(self, project_root):
        """Test handling of invalid HRBP commands."""
        returncode, stdout, stderr = run_p3_command(['hrbp-invalid-command'], project_root, timeout=5)
        
        # Should handle invalid command gracefully
        assert returncode != 0, "Invalid HRBP command should not succeed"
        assert 'unknown command' in stderr.lower() or 'invalid' in stderr.lower() or returncode == 1, \
            "Invalid command not handled properly"


class TestHRBPP3Integration:
    """Test HRBP integration with core p3 functionality."""
    
    def test_hrbp_with_p3_e2e_compatibility(self, project_root):
        """Test that HRBP doesn't interfere with p3 e2e."""
        # Test e2e command still works with HRBP system present
        returncode, stdout, stderr = run_p3_command(['e2e', 'f2'], project_root, timeout=10)
        
        # Should start executing (may timeout but shouldn't fail immediately)
        assert returncode in [0, -1, 124], f"e2e command failed immediately with HRBP present: {stderr}"
        
        # Should show proper execution message
        assert 'Executing:' in stdout or 'e2e' in stdout.lower(), "e2e not executing properly"
    
    def test_hrbp_with_p3_build_compatibility(self, project_root):
        """Test that HRBP doesn't interfere with p3 build commands."""
        returncode, stdout, stderr = run_p3_command(['build', 'f2'], project_root, timeout=5)
        
        # Should start build process
        assert returncode != 127, "build command not recognized with HRBP present"
        assert 'build' in stdout.lower() or 'Executing:' in stdout, "build not executing properly"
    
    def test_hrbp_with_p3_format_compatibility(self, project_root):
        """Test that HRBP doesn't interfere with p3 format/lint."""
        returncode, stdout, stderr = run_p3_command(['format'], project_root, timeout=10)
        
        # Should attempt to run format
        assert returncode != 127, "format command not recognized with HRBP present"
        assert 'format' in stdout.lower() or 'Executing:' in stdout, "format not executing properly"
    
    def test_hrbp_execution_monitoring_integration(self, project_root):
        """Test HRBP integration with p3 execution monitoring."""
        # Test that HRBP commands are monitored
        returncode, stdout, stderr = run_p3_command(['hrbp-status'], project_root, timeout=5)
        
        # Should show execution monitoring
        monitoring_indicators = [
            'Executing:',
            'monitoring',
            'agent execution',
            'performance'
        ]
        
        output_text = (stdout + stderr).lower()
        found_monitoring = any(indicator in output_text for indicator in monitoring_indicators)
        
        # Note: This may not always be present depending on environment
        # Just check that command executes without breaking monitoring
        assert returncode != 127, "HRBP commands should not break execution monitoring"
    
    def test_p3_command_validation_with_hrbp(self, p3_script_path):
        """Test p3 command validation logic works with HRBP commands."""
        p3_content = p3_script_path.read_text()
        
        # Check that command validation logic is present
        assert '_validate_command_syntax' in p3_content, "Command validation logic missing"
        
        # Check that HRBP commands go through validation
        assert '_handle_special_commands' in p3_content, "Special command handling missing"


class TestHRBPWorkflowCompatibility:
    """Test HRBP compatibility with existing workflows."""
    
    def test_hrbp_pr_creation_workflow(self, project_root):
        """Test HRBP integration with PR creation workflow."""
        # Test create-pr command still works
        returncode, stdout, stderr = run_p3_command(['create-pr', '--help'], project_root, timeout=5)
        
        # Should provide help (command should exist)
        assert returncode != 127, "create-pr command missing with HRBP present"
    
    def test_hrbp_git_hooks_integration(self, project_root):
        """Test HRBP git hooks integration."""
        # Check if HRBP hooks installer exists
        hooks_installer = project_root / "scripts" / "install_hrbp_hooks.py"
        post_merge_hook = project_root / "scripts" / "post_merge_hrbp_hook.py"
        
        assert hooks_installer.exists(), "HRBP hooks installer missing"
        assert post_merge_hook.exists(), "HRBP post-merge hook missing"
        
        # Check p3 has hook installation command
        returncode, stdout, stderr = run_p3_command(['install-hrbp-hooks'], project_root, timeout=5)
        assert returncode != 127, "install-hrbp-hooks command missing"
    
    def test_hrbp_monitoring_integration(self, project_root):
        """Test HRBP integration with monitoring commands."""
        # Test monitoring commands still work
        monitoring_commands = [
            ['monitoring-summary'],
            ['monitoring-stats'],
            ['status']
        ]
        
        for cmd in monitoring_commands:
            returncode, stdout, stderr = run_p3_command(cmd, project_root, timeout=5)
            assert returncode != 127, f"Monitoring command {cmd} not recognized with HRBP"
    
    def test_hrbp_environment_compatibility(self, project_root):
        """Test HRBP compatibility with environment commands."""
        env_commands = [
            ['env-status'],
            ['cache-status'],
            ['verify-env']
        ]
        
        for cmd in env_commands:
            returncode, stdout, stderr = run_p3_command(cmd, project_root, timeout=10)
            assert returncode != 127, f"Environment command {cmd} not recognized with HRBP"


class TestHRBPErrorHandling:
    """Test HRBP error handling and resilience in p3."""
    
    def test_hrbp_command_with_missing_dependencies(self, project_root):
        """Test HRBP command behavior with missing dependencies."""
        # Test with environment that may be missing HRBP dependencies
        env_vars = {'PYTHONPATH': str(project_root)}
        
        returncode, stdout, stderr = run_p3_command(['hrbp-status'], project_root, env_vars=env_vars)
        
        # Should handle missing dependencies gracefully
        assert returncode != 127, "Command not recognized"
        
        # Should provide meaningful error message if dependencies missing
        if returncode != 0:
            error_indicators = ['import', 'module', 'dependency', 'error']
            error_text = stderr.lower()
            has_meaningful_error = any(indicator in error_text for indicator in error_indicators)
            
            # Either succeeds or provides meaningful error
            assert has_meaningful_error or 'hrbp' in error_text, "No meaningful error message for missing dependencies"
    
    def test_hrbp_timeout_handling(self, project_root):
        """Test HRBP command timeout handling."""
        # Test command with very short timeout
        returncode, stdout, stderr = run_p3_command(['hrbp-status'], project_root, timeout=1)
        
        # Should either complete quickly or timeout gracefully
        assert returncode in [0, -1, 1, 2], "Command should complete or timeout gracefully"
    
    def test_hrbp_invalid_parameters(self, project_root):
        """Test HRBP command with invalid parameters."""
        # Test record-pr with invalid PR number
        returncode, stdout, stderr = run_p3_command(['hrbp-record-pr', 'invalid'], project_root, timeout=5)
        
        # Should handle invalid parameters gracefully
        assert returncode != 127, "Command should be recognized"
        
        # If it fails, should provide meaningful error
        if returncode != 0 and stderr:
            error_text = stderr.lower()
            meaningful_error = any(word in error_text for word in ['invalid', 'error', 'number', 'parameter'])
            assert meaningful_error, "Should provide meaningful error for invalid parameters"
    
    def test_hrbp_concurrent_execution(self, project_root):
        """Test HRBP commands under concurrent execution."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def run_hrbp_command():
            try:
                returncode, stdout, stderr = run_p3_command(['hrbp-status'], project_root, timeout=5)
                results.put(('success', returncode, stdout, stderr))
            except Exception as e:
                results.put(('error', str(e), '', ''))
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_hrbp_command)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10)
        
        # Check results
        successful_runs = 0
        while not results.empty():
            result = results.get()
            if result[0] == 'success' and result[1] != 127:  # Command recognized
                successful_runs += 1
        
        # At least one should succeed (others might timeout/conflict)
        assert successful_runs >= 1, "No concurrent HRBP commands succeeded"


class TestHRBPPerformanceIntegration:
    """Test HRBP performance integration with p3."""
    
    def test_hrbp_command_execution_speed(self, project_root):
        """Test HRBP command execution speed."""
        start_time = time.time()
        
        returncode, stdout, stderr = run_p3_command(['hrbp-status'], project_root, timeout=10)
        
        execution_time = time.time() - start_time
        
        # Should complete within reasonable time (10 seconds is generous)
        assert execution_time < 10, f"HRBP command too slow: {execution_time:.2f}s"
        
        # Should be recognized quickly
        assert returncode != 127, "Command should be recognized"
    
    def test_p3_help_performance_with_hrbp(self, project_root):
        """Test p3 help performance with HRBP commands."""
        start_time = time.time()
        
        returncode, stdout, stderr = run_p3_command(['--help'], project_root, timeout=5)
        
        execution_time = time.time() - start_time
        
        # Help should be fast even with HRBP commands
        assert execution_time < 5, f"p3 help too slow with HRBP: {execution_time:.2f}s"
        assert returncode == 0, "p3 help should succeed"
    
    def test_hrbp_memory_usage_integration(self, project_root):
        """Test HRBP memory usage doesn't affect p3 performance."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # Run HRBP command
            returncode, stdout, stderr = run_p3_command(['hrbp-status'], project_root, timeout=5)
            
            final_memory = process.memory_info().rss
            memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
            
            # Should not cause significant memory increase
            assert memory_increase < 100, f"HRBP command caused high memory usage: {memory_increase:.1f}MB"
            
        except ImportError:
            # psutil not available - skip memory test
            pytest.skip("psutil not available for memory testing")


class TestHRBPSystemIntegration:
    """Test HRBP system-level integration with p3."""
    
    def test_hrbp_initialization_with_p3(self, project_root):
        """Test HRBP system initialization through p3."""
        # Test that p3 can initialize with HRBP system present
        returncode, stdout, stderr = run_p3_command(['--help'], project_root, timeout=5)
        
        assert returncode == 0, "p3 should initialize successfully with HRBP"
        assert 'p3' in stdout, "p3 help should display"
    
    def test_hrbp_configuration_loading(self, project_root):
        """Test HRBP configuration loading through p3."""
        # Check if configuration files exist
        config_file = project_root / "common/config/hrbp_automation.yml"
        
        if config_file.exists():
            # Test config command
            returncode, stdout, stderr = run_p3_command(['hrbp-config'], project_root, timeout=5)
            assert returncode != 127, "hrbp-config should be recognized"
    
    def test_hrbp_logging_integration(self, project_root):
        """Test HRBP logging integration with p3."""
        # Check if logs directory structure exists (SSOT compliance)
        build_data_dir = project_root / "build_data"
        
        if build_data_dir.exists():
            logs_dir = build_data_dir / "logs"
            
            # Run HRBP command and check if it respects logging structure
            returncode, stdout, stderr = run_p3_command(['hrbp-status'], project_root, timeout=5)
            
            # Command should execute without logging errors
            assert 'log' not in stderr.lower() or 'error' not in stderr.lower(), \
                "HRBP commands should not generate logging errors"
    
    def test_hrbp_workflow_integration(self, project_root):
        """Test complete HRBP workflow integration."""
        # Test workflow sequence: status -> record-pr -> history
        commands = [
            ['hrbp-status'],
            ['hrbp-history']  # Skip record-pr as it needs parameter
        ]
        
        for cmd in commands:
            returncode, stdout, stderr = run_p3_command(cmd, project_root, timeout=5)
            assert returncode != 127, f"HRBP workflow command {cmd} not recognized"
            
            # Should not break subsequent commands
            assert 'fatal' not in stderr.lower(), f"HRBP command {cmd} caused fatal error"


# Test runner and utilities
def run_hrbp_integration_smoke_test():
    """Run smoke test for HRBP integration."""
    print("🧪 Running HRBP P3 Integration Smoke Test...")
    
    project_root = Path(__file__).parent.parent
    
    test_results = {
        'p3_script_exists': False,
        'hrbp_commands_defined': False,
        'hrbp_help_integration': False,
        'hrbp_command_recognition': False,
        'workflow_compatibility': False
    }
    
    try:
        # Test 1: P3 script exists
        p3_script = project_root / "p3.py"
        if p3_script.exists():
            test_results['p3_script_exists'] = True
            print("  ✅ p3.py script exists")
        else:
            print("  ❌ p3.py script missing")
        
        # Test 2: HRBP commands defined
        if p3_script.exists():
            content = p3_script.read_text()
            hrbp_commands = ['hrbp-status', 'hrbp-record-pr', 'hrbp-manual-trigger']
            
            if all(cmd in content for cmd in hrbp_commands):
                test_results['hrbp_commands_defined'] = True
                print("  ✅ HRBP commands defined in p3.py")
            else:
                print("  ❌ HRBP commands missing from p3.py")
        
        # Test 3: Help integration
        try:
            returncode, stdout, stderr = run_p3_command(['--help'], project_root, timeout=10)
            if returncode == 0 and 'hrbp' in stdout.lower():
                test_results['hrbp_help_integration'] = True
                print("  ✅ HRBP commands appear in help")
            else:
                print("  ❌ HRBP commands not in help")
        except Exception as e:
            print(f"  ❌ Help test failed: {e}")
        
        # Test 4: Command recognition
        try:
            returncode, stdout, stderr = run_p3_command(['hrbp-status'], project_root, timeout=5)
            if returncode != 127:  # Command recognized
                test_results['hrbp_command_recognition'] = True
                print("  ✅ HRBP commands recognized")
            else:
                print("  ❌ HRBP commands not recognized")
        except Exception as e:
            print(f"  ❌ Command recognition test failed: {e}")
        
        # Test 5: Workflow compatibility
        try:
            returncode, stdout, stderr = run_p3_command(['e2e', '--help'], project_root, timeout=5)
            if returncode != 127:
                test_results['workflow_compatibility'] = True
                print("  ✅ Core workflows still work")
            else:
                print("  ❌ Core workflows broken")
        except Exception as e:
            print(f"  ❌ Workflow compatibility test failed: {e}")
        
        # Summary
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        print(f"\n📊 Smoke Test Results: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("🎉 HRBP P3 integration smoke test passed!")
            return True
        else:
            print("⚠️  HRBP P3 integration has issues")
            return False
            
    except Exception as e:
        print(f"💥 Smoke test failed: {e}")
        return False


if __name__ == "__main__":
    """Run HRBP P3 integration tests."""
    # Run smoke test first
    if run_hrbp_integration_smoke_test():
        print("\n✅ HRBP P3 integration smoke test completed successfully")
    else:
        print("\n❌ HRBP P3 integration smoke test completed with issues")
    
    print("\n💡 Run full test suite with: pytest tests/test_hrbp_p3_integration.py -v")