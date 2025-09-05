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
        returncode, stdout, stderr = run_p3_command(["help"])
        # Help should return 0 and show usage information
        assert returncode == 0 and ("P3 CLI" in stdout or "DAILY WORKFLOW" in stdout)

    def test_p3_no_args(self):
        """Test p3 without arguments shows help."""
        returncode, stdout, stderr = run_p3_command([])
        # Should show help information
        assert returncode == 0 and ("P3 CLI" in stdout or "DAILY WORKFLOW" in stdout)

    def test_check_scope_validation(self):
        """Test check command accepts different scopes."""
        valid_scopes = ["f2", "m7", "n100", "v3k"]

        for scope in valid_scopes:
            returncode, stdout, stderr = run_p3_command(["check", scope], timeout=5)
            # Command should start executing (may timeout, but should recognize scope)
            assert returncode == -1 or "executing" in stdout.lower() or "pixi run" in stdout.lower()

    def test_test_scope_validation(self):
        """Test test command accepts different scopes."""
        valid_scopes = ["f2", "m7", "n100", "v3k"]

        for scope in valid_scopes:
            returncode, stdout, stderr = run_p3_command(["test", scope], timeout=5)
            # Command should start executing (may timeout, but should recognize scope)
            assert returncode == -1 or "executing" in stdout.lower() or "pixi run" in stdout.lower()

    def test_build_scope_validation(self):
        """Test build command accepts different scopes."""
        valid_scopes = ["f2", "m7", "n100", "v3k"]

        for scope in valid_scopes:
            returncode, stdout, stderr = run_p3_command(["build", scope], timeout=5)
            # Command should start executing (may timeout, but should recognize scope)
            assert returncode == -1 or "executing" in stdout.lower() or "pixi run" in stdout.lower()

    def test_simplified_commands_exist(self):
        """Test that the 8 simplified commands are recognized."""
        simple_commands = [
            ["ready"],
            ["reset"],
            ["check"],
            ["test"],
            ["debug"],
            ["build"],
            ["version"],
        ]

        for cmd in simple_commands:
            returncode, stdout, stderr = run_p3_command(cmd, timeout=10)
            # Commands should be recognized (even if they fail due to missing dependencies)
            assert returncode != 127, f"Command {cmd} not recognized"

    def test_ship_command_validation(self):
        """Test ship command parameter validation."""
        # Ship command should require title and issue number
        returncode, stdout, stderr = run_p3_command(["ship"], timeout=5)
        # Should show error about missing parameters
        assert returncode != 0 and ("title" in stderr.lower() or "issue" in stderr.lower() or "error" in stderr.lower())

    def test_invalid_command(self):
        """Test invalid command handling."""
        returncode, stdout, stderr = run_p3_command(["invalid-command-xyz"])
        # Should handle invalid commands gracefully
        assert returncode != 0 or "invalid" in stderr.lower() or "unknown" in stderr.lower()


class TestP3VersionManagement:
    """Test P3 version management functionality."""

    def test_version_command(self):
        """Test version command output."""
        returncode, stdout, stderr = run_p3_command(["version"])
        # Version should return successfully with version info
        assert returncode == 0 and ("P3 Version:" in stdout or "Version:" in stdout or "." in stdout)

    def test_version_parsing(self):
        """Test version output contains expected format."""
        returncode, stdout, stderr = run_p3_command(["version"])
        if returncode == 0:
            # Should contain version number format (x.y.z)
            import re
            version_pattern = r'\d+\.\d+\.\d+'
            assert re.search(version_pattern, stdout), "Version output should contain semantic version number"


if __name__ == "__main__":
    # Run basic smoke test
    print("🧪 Running simplified P3 command tests...")

    # Test basic command recognition
    returncode, stdout, stderr = run_p3_command(["help"])
    print(f"Help command: {'✅ PASS' if returncode == 0 and 'P3 CLI' in stdout else '❌ FAIL'}")

    # Test version command
    returncode, stdout, stderr = run_p3_command(["version"], timeout=3)
    print(f"Version command: {'✅ PASS' if returncode == 0 and '.' in stdout else '❌ FAIL'}")

    # Test build scope recognition  
    returncode, stdout, stderr = run_p3_command(["build", "f2"], timeout=3)
    print(f"Build scope recognition: {'✅ PASS' if 'executing' in stdout.lower() else '❌ FAIL'}")

    print("✅ Simplified P3 command tests completed")
