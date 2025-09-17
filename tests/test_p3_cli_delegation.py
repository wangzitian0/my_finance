#!/usr/bin/env python3
"""
Comprehensive tests for P3 CLI delegation pattern and SSOT integration.

Tests cover:
1. P3 CLI delegation from root to infra/p3/p3.py
2. SSOT I/O enforcement through directory_manager
3. Backward compatibility and functionality
4. Command routing and validation
5. Error handling and diagnostics

Issue #288: PR Review feedback implementation tests
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from common.core.directory_manager import DirectoryManager
    from infra.p3.p3 import P3CLI, get_version_string
except ImportError as e:
    print(f"Warning: Import failed - {e}")
    P3CLI = None
    DirectoryManager = None


class TestP3CLIDelegation(unittest.TestCase):
    """Test P3 CLI delegation pattern and SSOT integration."""

    def setUp(self):
        """Set up test environment."""
        self.test_root = Path(__file__).parent.parent

        if P3CLI is None:
            self.skipTest("P3CLI not available for testing")

    def test_p3_cli_initialization(self):
        """Test P3CLI initialization with DirectoryManager integration."""
        cli = P3CLI()

        # Verify SSOT integration
        self.assertTrue(hasattr(cli, "directory_manager"))
        self.assertTrue(hasattr(cli, "project_root"))
        self.assertIsInstance(cli.project_root, Path)

        # Verify command loading
        self.assertIsInstance(cli.commands, dict)
        self.assertIn("ready", cli.commands)
        self.assertIn("test", cli.commands)
        self.assertIn("ship", cli.commands)

    def test_version_string_generation(self):
        """Test version string generation."""
        version = get_version_string()
        self.assertIsInstance(version, str)
        self.assertTrue(len(version) > 0)
        self.assertIn("2.0.1", version)

    def test_command_validation(self):
        """Test command validation and error handling."""
        cli = P3CLI()

        # Valid commands should exist
        valid_commands = ["ready", "stop", "reset", "check", "test", "ship", "build", "version"]
        for cmd in valid_commands:
            self.assertIn(cmd, cli.commands, f"Command '{cmd}' should be available")

    @patch("subprocess.run")
    def test_git_branch_detection(self, mock_run):
        """Test git branch detection with SSOT subprocess execution."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "feature/test-branch\n"
        mock_run.return_value = mock_result

        cli = P3CLI()
        branch = cli._get_current_branch()

        self.assertEqual(branch, "feature/test-branch")

    @patch("subprocess.run")
    def test_git_branch_fallback(self, mock_run):
        """Test git branch detection fallback on failure."""
        mock_run.side_effect = Exception("Git not available")

        cli = P3CLI()
        branch = cli._get_current_branch()

        self.assertEqual(branch, "unknown")

    def test_command_mapping_completeness(self):
        """Test that all essential commands are mapped correctly."""
        cli = P3CLI()

        expected_commands = {
            "ready": "python infra/system/workflow_ready.py",
            "stop": "python infra/system/workflow_stop.py",
            "reset": "python infra/system/workflow_reset.py",
            "check": "python infra/development/workflow_check.py",
            "test": "python infra/scripts/utilities/run_test.py",
            "ship": "python infra/workflows/pr_creation.py",
            "build": "python ETL/build_dataset.py",
            "version": "version_command",
        }

        for cmd, expected_script in expected_commands.items():
            self.assertEqual(
                cli.commands[cmd],
                expected_script,
                f"Command '{cmd}' should map to '{expected_script}'",
            )

    def test_directory_manager_integration(self):
        """Test DirectoryManager integration for SSOT I/O enforcement."""
        if DirectoryManager is None:
            self.skipTest("DirectoryManager not available for testing")

        cli = P3CLI()

        # Verify DirectoryManager instance exists
        self.assertIsNotNone(cli.directory_manager)
        self.assertIsInstance(cli.directory_manager, DirectoryManager)

        # Verify project root is set correctly
        self.assertEqual(cli.project_root, cli.directory_manager.root_path)

    def test_backward_compatibility(self):
        """Test that delegation maintains backward compatibility."""
        # Test that root p3.py still exists and delegates properly
        root_p3_path = self.test_root / "p3.py"
        if root_p3_path.exists():
            # Root delegation should work
            self.assertTrue(root_p3_path.is_file())

            # Read and verify delegation content
            with open(root_p3_path, "r") as f:
                content = f.read()
                self.assertIn("from infra.p3.p3 import main", content)

    @patch("os.chdir")
    @patch("subprocess.run")
    def test_command_execution_flow(self, mock_run, mock_chdir):
        """Test command execution flow with mocked subprocess."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        cli = P3CLI()

        # Test version command (doesn't use subprocess)
        with patch("builtins.print") as mock_print:
            cli.run("version", [])
            mock_print.assert_called()

    def test_scope_handling(self):
        """Test scope argument handling for test/build/check commands."""
        cli = P3CLI()

        # Commands that should accept scope arguments
        scope_commands = ["test", "build", "check"]
        for cmd in scope_commands:
            self.assertIn(cmd, cli.commands)

    @patch("subprocess.run")
    def test_ssot_subprocess_integration(self, mock_run):
        """Test SSOT subprocess execution integration."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "success"
        mock_run.return_value = mock_result

        cli = P3CLI()

        # Test that DirectoryManager subprocess methods are used when available
        if hasattr(cli, "directory_manager") and cli.directory_manager:
            branch = cli._get_current_branch()
            # Should not raise exception and should return reasonable result
            self.assertIsInstance(branch, str)

    def test_error_diagnostics(self):
        """Test error diagnostic messages for different command failures."""
        cli = P3CLI()

        # Test that help message is comprehensive
        with patch("builtins.print") as mock_print:
            cli.print_help()
            mock_print.assert_called()

            # Verify help content mentions all main commands
            help_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
            help_text = " ".join(str(call) for call in help_calls)

            essential_commands = ["ready", "test", "ship", "version"]
            for cmd in essential_commands:
                self.assertIn(cmd, help_text, f"Help should mention '{cmd}' command")


class TestP3CLIFunctionality(unittest.TestCase):
    """Test P3 CLI functionality and integration points."""

    def setUp(self):
        """Set up test environment."""
        if P3CLI is None:
            self.skipTest("P3CLI not available for testing")

    def test_help_command_completeness(self):
        """Test that help command provides comprehensive information."""
        cli = P3CLI()

        with patch("builtins.print") as mock_print:
            cli.print_help()

            # Verify all command categories are covered
            help_output = str(mock_print.call_args_list)

            # Check for essential sections
            essential_sections = ["DAILY WORKFLOW", "TROUBLESHOOTING", "SCOPES"]
            for section in essential_sections:
                self.assertIn(section, help_output)

    @patch("sys.exit")
    def test_invalid_command_handling(self, mock_exit):
        """Test handling of invalid commands."""
        cli = P3CLI()

        # Mock sys.exit to prevent actual exit
        mock_exit.side_effect = SystemExit(1)

        with patch("builtins.print") as mock_print:
            with self.assertRaises(SystemExit):
                cli.run("invalid_command", [])

            # Should print error message
            mock_print.assert_called()
            mock_exit.assert_called_with(1)

    def test_ship_command_validation(self):
        """Test ship command argument validation."""
        cli = P3CLI()

        with patch("sys.exit") as mock_exit, patch("builtins.print") as mock_print:
            # Mock sys.exit to prevent actual exit
            mock_exit.side_effect = SystemExit(1)

            with self.assertRaises(SystemExit):
                # Ship command without arguments should fail
                cli.run("ship", [])

            mock_exit.assert_called_with(1)
            # Should print usage information
            mock_print.assert_called()

    def test_modular_architecture_compliance(self):
        """Test that P3 CLI follows L1/L2 modular architecture."""
        cli = P3CLI()

        # All commands should reference modular paths (infra/, ETL/, etc.)
        for command, script_path in cli.commands.items():
            if command == "version":
                continue  # Special case

            # Should use modular L1 directories
            l1_modules = ["infra/", "ETL/", "scripts/"]
            path_uses_l1 = any(l1_mod in script_path for l1_mod in l1_modules)

            self.assertTrue(
                path_uses_l1, f"Command '{command}' should use L1 modular path, got: {script_path}"
            )


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)
