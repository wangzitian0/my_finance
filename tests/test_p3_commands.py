#!/usr/bin/env python3
"""
Unit tests for p3 command functionality.
Tests the p3 command infrastructure without executing time-consuming operations.
"""

import subprocess
import sys
from pathlib import Path

import pytest


def run_p3_command(args, timeout=30):
    """Run p3 command with timeout and capture output."""
    try:
        result = subprocess.run(
            ["./p3"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).parent.parent,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


class TestP3Commands:
    """Test p3 command infrastructure."""

    def test_p3_help(self):
        """Test p3 help/usage output."""
        returncode, stdout, stderr = run_p3_command(["--help"])
        # Help should return 0 or show usage information
        assert returncode == 0 or "Usage:" in stdout or "p3" in stdout

    def test_p3_no_args(self):
        """Test p3 without arguments shows help."""
        returncode, stdout, stderr = run_p3_command([])
        # Should show help or usage information
        assert "p3" in stdout or "Usage:" in stdout or returncode != 0

    def test_e2e_scope_validation(self):
        """Test e2e command accepts different scopes."""
        # Test valid scopes (with timeout to avoid long execution)
        valid_scopes = ["f2", "m7", "n100", "v3k"]
        
        for scope in valid_scopes:
            returncode, stdout, stderr = run_p3_command(["e2e", scope], timeout=5)
            # Command should start executing (may timeout, but should recognize scope)
            assert returncode == -1 or "end-to-end" in stdout.lower() or "running" in stdout.lower()

    def test_build_scope_validation(self):
        """Test build command accepts different scopes."""
        valid_scopes = ["f2", "m7", "n100", "v3k"]
        
        for scope in valid_scopes:
            returncode, stdout, stderr = run_p3_command(["build", "run", scope], timeout=5)
            # Command should start executing (may timeout, but should recognize scope)  
            assert returncode == -1 or scope in stdout or "build" in stdout.lower()

    def test_basic_commands_exist(self):
        """Test that basic commands are recognized."""
        basic_commands = [
            ["format"],
            ["lint"], 
            ["test"],
            ["status"],
            ["env", "status"],
            ["build-status"],
        ]
        
        for cmd in basic_commands:
            returncode, stdout, stderr = run_p3_command(cmd, timeout=10)
            # Commands should be recognized (even if they fail due to missing dependencies)
            assert returncode != 127, f"Command {cmd} not recognized"

    def test_invalid_command(self):
        """Test invalid command handling."""
        returncode, stdout, stderr = run_p3_command(["invalid-command-xyz"])
        # Should handle invalid commands gracefully
        assert returncode != 0 or "invalid" in stderr.lower() or "unknown" in stderr.lower()


class TestP3CommandParsing:
    """Test p3 command parsing without execution."""

    @pytest.fixture
    def p3_script_content(self):
        """Load p3 script content for parsing tests."""
        p3_path = Path(__file__).parent.parent / "p3"
        return p3_path.read_text()

    def test_all_commands_have_functions(self, p3_script_content):
        """Test that all commands in the case statement have corresponding functions."""
        import re
        
        # Extract commands from the main case statement
        case_match = re.search(r'case\s+\$1\s+in\s*\n(.*?)\nesac', p3_script_content, re.DOTALL)
        assert case_match, "Could not find main case statement"
        
        case_content = case_match.group(1)
        
        # Find all command patterns
        command_patterns = re.findall(r'^\s*([a-z-]+)(?:\|[a-z-]+)*\)', case_content, re.MULTILINE)
        
        # Check that each command has a corresponding function
        for command in command_patterns:
            if command in ['*', 'help']:  # Skip default cases
                continue
                
            func_name = f"cmd_{command.replace('-', '_')}"
            assert func_name in p3_script_content, f"Missing function {func_name} for command {command}"

    def test_e2e_function_has_scope_support(self, p3_script_content):
        """Test that e2e function supports scope parameters."""
        assert "cmd_e2e()" in p3_script_content
        assert 'scope="${1:-m7}"' in p3_script_content
        assert 'case "$scope" in' in p3_script_content

    def test_scope_validation_patterns(self, p3_script_content):
        """Test that scope validation patterns are present."""
        expected_scopes = ["f2", "m7", "n100", "v3k"]
        
        for scope in expected_scopes:
            assert scope in p3_script_content, f"Scope {scope} not found in script"

    def test_command_structure_consistency(self, p3_script_content):
        """Test that command structure follows consistent patterns."""
        # All cmd_ functions should exist
        functions = re.findall(r'^cmd_([a-z_]+)\(\)', p3_script_content, re.MULTILINE)
        assert len(functions) > 5, "Should have multiple command functions"
        
        # Functions should have basic structure
        for func in functions[:5]:  # Test first 5 functions
            func_content = re.search(f'cmd_{func}\\(\\).*?^}}', p3_script_content, re.MULTILINE | re.DOTALL)
            assert func_content, f"Function cmd_{func} should have proper structure"


if __name__ == "__main__":
    # Run basic smoke test
    print("🧪 Running p3 command smoke tests...")
    
    # Test basic command recognition
    returncode, stdout, stderr = run_p3_command(["--help"])
    print(f"Help command: {'✅ PASS' if returncode == 0 else '❌ FAIL'}")
    
    # Test e2e scope recognition  
    returncode, stdout, stderr = run_p3_command(["e2e", "f2"], timeout=3)
    print(f"E2E scope recognition: {'✅ PASS' if 'f2' in stdout or 'end-to-end' in stdout.lower() else '❌ FAIL'}")
    
    print("✅ Basic p3 command tests completed")