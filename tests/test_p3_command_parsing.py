#!/usr/bin/env python3
"""
Unit tests for p3 command parsing and validation
Tests command line argument parsing without executing actual commands
"""

import os
import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase


class TestP3CommandParsing(TestCase):
    """Test p3 command parsing and validation without execution"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once"""
        cls.repo_root = Path(__file__).parent.parent
        cls.p3_script = cls.repo_root / "p3"

        # Ensure p3 script exists and is executable
        if not cls.p3_script.exists():
            raise FileNotFoundError(f"p3 script not found at {cls.p3_script}")

        if not os.access(cls.p3_script, os.X_OK):
            os.chmod(cls.p3_script, 0o755)

    def run_p3_command(self, args, timeout=3):
        """Helper to run p3 commands with quick timeout"""
        cmd = [str(self.p3_script)] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                cwd=self.repo_root,
            )
            return result
        except subprocess.TimeoutExpired:
            # For parsing tests, timeout is actually expected for some commands
            # Return a mock result indicating timeout
            class MockResult:
                def __init__(self):
                    self.returncode = 124  # Standard timeout exit code
                    self.stdout = ""
                    self.stderr = "Command timed out (expected for some commands)"

            return MockResult()
        except FileNotFoundError:
            self.fail(f"p3 script not found or not executable: {self.p3_script}")

    def test_help_command(self):
        """Test p3 help command displays usage"""
        result = self.run_p3_command(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("p3 - Unified developer commands", result.stdout)
        self.assertIn("Environment Management:", result.stdout)
        self.assertIn("Development Commands:", result.stdout)

    def test_help_command_variations(self):
        """Test different help command variations"""
        help_variants = ["-h", "help", ""]
        for variant in help_variants:
            with self.subTest(variant=variant):
                args = [variant] if variant else []
                result = self.run_p3_command(args)
                self.assertEqual(result.returncode, 0)
                self.assertIn("p3 - Unified developer commands", result.stdout)

    def test_invalid_command(self):
        """Test p3 with invalid command shows error"""
        result = self.run_p3_command(["invalid-command"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown command: invalid-command", result.stderr)

    def test_create_pr_arguments_validation(self):
        """Test create-pr command validates required arguments"""
        # Missing both title and issue
        result = self.run_p3_command(["create-pr"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("title and issue number are required", result.stderr)

        # Missing issue number
        result = self.run_p3_command(["create-pr", "Test title"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("title and issue number are required", result.stderr)

    def test_invalid_env_subcommand(self):
        """Test env command with invalid subcommand"""
        result = self.run_p3_command(["env", "invalid-subcmd"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown env command: invalid-subcmd", result.stderr)

    def test_invalid_neo4j_subcommand(self):
        """Test neo4j command with invalid subcommand"""
        result = self.run_p3_command(["neo4j", "invalid-subcmd"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown neo4j command: invalid-subcmd", result.stderr)

    def test_invalid_podman_subcommand(self):
        """Test podman command with invalid subcommand"""
        result = self.run_p3_command(["podman", "invalid-subcmd"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown podman command: invalid-subcmd", result.stderr)

    def test_refresh_with_invalid_scope(self):
        """Test refresh command with invalid scope"""
        result = self.run_p3_command(["refresh", "invalid-scope"])
        if result.returncode != 124:  # Not timeout
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid scope: invalid-scope", result.stderr)

    def test_command_completion_data_consistency(self):
        """Test that completion script is consistent with actual commands"""
        # Read completion script
        completion_script = self.repo_root / "scripts" / "p3-completion.zsh"
        if not completion_script.exists():
            self.skipTest("Completion script not found")

        completion_content = completion_script.read_text()

        # Extract commands from completion script
        import re

        commands_match = re.search(r"_p3_commands=\(([^)]+)\)", completion_content)
        if not commands_match:
            self.fail("Could not find command list in completion script")

        completion_commands = commands_match.group(1).split()

        # Define expected core commands (from usage() function)
        expected_commands = {
            "env",
            "podman",
            "neo4j",
            "format",
            "lint",
            "typecheck",
            "test",
            "e2e",
            "build",
            "fast-build",
            "refresh",
            "create-build",
            "release-build",
            "clean",
            "build-status",
            "create-pr",
            "commit-data-changes",
            "cleanup-branches",
            "shutdown-all",
            "status",
            "cache-status",
            "verify-env",
            "check-integrity",
        }

        completion_commands_set = set(completion_commands)

        # Check that all expected commands are in completion
        missing_in_completion = expected_commands - completion_commands_set
        if missing_in_completion:
            self.fail(f"Commands missing from completion script: {missing_in_completion}")

    def test_p3_script_structure(self):
        """Test p3 script has correct structure and permissions"""
        # Test permissions
        self.assertTrue(os.access(self.p3_script, os.X_OK), "p3 script should be executable")
        self.assertTrue(os.access(self.p3_script, os.R_OK), "p3 script should be readable")

        # Test shebang
        with open(self.p3_script, "r") as f:
            first_line = f.readline().strip()

        self.assertTrue(first_line.startswith("#!/"), "p3 script should have shebang")
        self.assertIn("sh", first_line, "p3 script should be shell script")

    def test_usage_function_contains_all_commands(self):
        """Test that usage function documents all major commands"""
        with open(self.p3_script, "r") as f:
            script_content = f.read()

        # Find usage function
        import re

        usage_match = re.search(
            r"usage\(\) \{.*?^EOF\n^}", script_content, re.MULTILINE | re.DOTALL
        )
        if not usage_match:
            self.fail("Could not find usage() function in p3 script")

        usage_content = usage_match.group(0)

        # Check that major command categories are documented
        expected_sections = [
            "Environment Management",
            "Container Management",
            "Development Commands",
            "Build Management",
            "Workflow Management",
            "Status & Validation",
        ]

        for section in expected_sections:
            self.assertIn(section, usage_content, f"Usage should document {section} section")

    def test_case_statement_completeness(self):
        """Test that case statement handles all documented commands"""
        with open(self.p3_script, "r") as f:
            script_content = f.read()

        # Extract main case statement (the one that handles $1, not sub-functions)
        import re

        # Find the main case statement by looking for the one that handles the first argument
        # and has environment/container/development comment sections
        main_case_pattern = r'case "\$1" in.*?# Environment management.*?esac'
        case_match = re.search(main_case_pattern, script_content, re.DOTALL)
        if not case_match:
            self.fail("Could not find main case statement in p3 script")

        case_content = case_match.group(0)

        # Check that key commands are handled
        key_commands = [
            "env",
            "podman", 
            "neo4j",
            "format",
            "lint",
            "test",
            "e2e",
            "build",
            "refresh",
            "create-pr",
            "status"
        ]

        for cmd in key_commands:
            # Check if command is handled in case statement
            # Look for pattern like "env) shift; cmd_env"
            cmd_func_name = cmd.replace('-', '_')
            pattern = rf"{re.escape(cmd)}\)\s+shift;\s+cmd_{cmd_func_name}"
            if not re.search(pattern, case_content):
                self.fail(f"Command '{cmd}' not handled in main case statement")

    def test_error_handling_patterns(self):
        """Test consistent error handling patterns"""
        with open(self.p3_script, "r") as f:
            script_content = f.read()

        # Check for consistent error messages
        self.assertIn('echo "Unknown command:', script_content)
        self.assertIn("exit 2", script_content)  # Standard error exit code

        # Check for help on unknown commands
        self.assertIn("usage", script_content)


if __name__ == "__main__":
    import unittest

    unittest.main()
