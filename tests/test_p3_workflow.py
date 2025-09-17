#!/usr/bin/env python3
"""
Simple unit tests for P3 workflow functionality
Tests the entire chain: PATH -> p3 script -> p3.py discovery -> command execution
"""

import os
import subprocess
from pathlib import Path

import pytest


class TestP3Workflow:
    """Test P3 command workflow and worktree compatibility"""

    def test_p3_in_path(self):
        """Test that p3 command is found in PATH"""
        result = subprocess.run(["which", "p3"], capture_output=True, text=True)
        assert result.returncode == 0, "p3 command not found in PATH"
        assert "my_finance/p3" in result.stdout, f"Unexpected p3 path: {result.stdout}"

    def test_p3_version_command(self):
        """Test p3 version command works"""
        result = subprocess.run(["p3", "version"], capture_output=True, text=True, timeout=10)
        assert result.returncode == 0, f"p3 version failed: {result.stderr}"
        assert "P3 Version:" in result.stdout, f"Version output unexpected: {result.stdout}"
        assert "feature/283-module-adjust-rebased" in result.stdout, "Should show current branch"

    def test_p3_script_discovery(self):
        """Test that p3 script correctly finds p3.py in current directory"""
        # Check p3.py exists in current directory
        p3_py_path = Path("./p3.py")
        assert p3_py_path.exists(), "p3.py should exist in worktree"

    def test_p3_worktree_isolation(self):
        """Test that p3 works correctly in worktree vs main repo"""
        # Get current worktree branch
        result = subprocess.run(["p3", "version"], capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
        assert "feature/283-module-adjust-rebased" in result.stdout, "Should show worktree branch"

        # Check working directory is correct
        assert (
            "worktree/feature-283-module-adjust" in result.stdout
        ), "Should show worktree directory"

    def test_p3_help_commands(self):
        """Test that p3 shows available commands"""
        result = subprocess.run(["p3", "help"], capture_output=True, text=True, timeout=10)
        assert (
            "Available commands:" in result.stdout or "DAILY WORKFLOW" in result.stdout
        ), "Should show available commands"
        expected_commands = ["ready", "stop", "reset", "check", "test", "ship", "build", "version"]
        for cmd in expected_commands:
            assert cmd in result.stdout, f"Command '{cmd}' missing from help"

    def test_p3_script_structure(self):
        """Test p3 script has correct structure"""
        with open("p3", "r") as f:
            content = f.read()

        # Check it's a bash script
        assert content.startswith("#!/bin/bash"), "p3 should be a bash script"

        # Check it searches for p3.py
        assert "p3.py" in content, "p3 script should search for p3.py"

        # Check it uses directory traversal
        assert 'while [[ "$dir" != "/" ]]' in content, "Should traverse directories"

        # Check it executes python
        assert "exec python p3.py" in content, "Should execute python p3.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
