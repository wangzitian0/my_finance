#!/usr/bin/env python3
"""
Unit tests for p3 command infrastructure
Tests shell command functionality, argument parsing, and command routing
"""

import os
import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch


class TestP3Commands(TestCase):
    """Test p3 shell command infrastructure"""

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

    def run_p3_command(self, args, check=False):
        """Helper to run p3 commands and capture output"""
        cmd = [str(self.p3_script)] + args
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=10,
                check=check,
                cwd=self.repo_root
            )
            return result
        except subprocess.TimeoutExpired:
            self.fail(f"Command timeout: {' '.join(cmd)}")
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

    def test_e2e_command_scope_parsing(self):
        """Test e2e command accepts different scopes"""
        # Since these tests run actual commands, we expect them to fail
        # but we want to ensure they fail at the pixi/command level, not argument parsing
        scopes = ["f2", "m7", "n100", "v3k"]
        
        for scope in scopes:
            with self.subTest(scope=scope):
                result = self.run_p3_command(["e2e", scope])
                
                # Command should not fail due to invalid scope argument parsing
                # It's OK if pixi/sh commands are missing, but scope should be accepted
                if result.returncode != 0:
                    # Check that error is about missing commands, not invalid scope
                    error_lower = result.stderr.lower()
                    valid_errors = any(err in error_lower for err in [
                        "no such file", "command not found", "pixi", "sh", "not found"
                    ])
                    invalid_scope_error = "invalid scope" in error_lower or "unknown" in error_lower
                    
                    if invalid_scope_error:
                        self.fail(f"e2e {scope} failed due to scope validation: {result.stderr}")
                    elif not valid_errors:
                        self.fail(f"e2e {scope} failed unexpectedly: {result.stderr}")

    def test_build_command_scope_parsing(self):
        """Test build command accepts different scopes and 'run' subcommand"""
        test_cases = [
            ["build", "f2"],
            ["build", "run", "m7"],
            ["refresh", "n100"],
            ["fast-build", "v3k"]
        ]
        
        for args in test_cases:
            with self.subTest(args=args):
                result = self.run_p3_command(args)
                
                if result.returncode != 0:
                    # Check that error is about missing commands, not invalid arguments
                    error_lower = result.stderr.lower()
                    valid_errors = any(err in error_lower for err in [
                        "no such file", "command not found", "pixi", "sh", "not found"
                    ])
                    invalid_arg_error = any(err in error_lower for err in [
                        "invalid scope", "unknown", "usage:", "error:"
                    ])
                    
                    if invalid_arg_error and not valid_errors:
                        self.fail(f"Command {' '.join(args)} failed due to argument parsing: {result.stderr}")

    def test_env_subcommands(self):
        """Test env subcommands are properly routed"""
        env_commands = ["setup", "start", "stop", "status", "reset"]
        
        for subcmd in env_commands:
            with self.subTest(subcmd=subcmd):
                result = self.run_p3_command(["env", subcmd])
                
                if result.returncode != 0:
                    # Check that error is about missing commands, not invalid subcommand
                    error_lower = result.stderr.lower()
                    valid_errors = any(err in error_lower for err in [
                        "no such file", "command not found", "pixi", "ansible", "sh", "not found"
                    ])
                    invalid_subcmd = f"unknown env command: {subcmd}" in error_lower
                    
                    if invalid_subcmd:
                        self.fail(f"env {subcmd} was not recognized as valid subcommand")
                    elif not valid_errors:
                        self.fail(f"env {subcmd} failed unexpectedly: {result.stderr}")

    def test_neo4j_subcommands(self):
        """Test neo4j subcommands are properly routed"""
        neo4j_commands = ["logs", "connect", "restart", "stop", "start"]
        
        for subcmd in neo4j_commands:
            with self.subTest(subcmd=subcmd):
                result = self.run_p3_command(["neo4j", subcmd])
                
                if result.returncode != 0:
                    # Check that error is about missing commands, not invalid subcommand
                    error_lower = result.stderr.lower()
                    valid_errors = any(err in error_lower for err in [
                        "no such file", "command not found", "pixi", "sh", "not found"
                    ])
                    invalid_subcmd = f"unknown neo4j command: {subcmd}" in error_lower
                    
                    if invalid_subcmd:
                        self.fail(f"neo4j {subcmd} was not recognized as valid subcommand")
                    elif not valid_errors:
                        self.fail(f"neo4j {subcmd} failed unexpectedly: {result.stderr}")

    def test_cleanup_branches_flags(self):
        """Test cleanup-branches command accepts flags"""
        flags = ["--dry-run", "--auto"]
        
        for flag in flags:
            with self.subTest(flag=flag):
                result = self.run_p3_command(["cleanup-branches", flag])
                
                if result.returncode != 0:
                    # Check that error is about missing commands, not invalid flag
                    error_lower = result.stderr.lower()
                    valid_errors = any(err in error_lower for err in [
                        "no such file", "command not found", "pixi", "sh", "not found"
                    ])
                    
                    if not valid_errors:
                        self.fail(f"cleanup-branches {flag} failed unexpectedly: {result.stderr}")

    def test_create_pr_arguments(self):
        """Test create-pr command validates required arguments"""
        # Missing both title and issue
        result = self.run_p3_command(["create-pr"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("title and issue number are required", result.stderr)
        
        # Missing issue number
        result = self.run_p3_command(["create-pr", "Test title"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("title and issue number are required", result.stderr)

    def test_command_completion_data_consistency(self):
        """Test that completion script is consistent with actual commands"""
        # Read completion script
        completion_script = self.repo_root / "scripts" / "p3-completion.zsh"
        if not completion_script.exists():
            self.skipTest("Completion script not found")
        
        completion_content = completion_script.read_text()
        
        # Extract commands from completion script
        import re
        commands_match = re.search(r'_p3_commands=\(([^)]+)\)', completion_content)
        if not commands_match:
            self.fail("Could not find command list in completion script")
        
        completion_commands = commands_match.group(1).split()
        
        # Define expected core commands (from usage() function)
        expected_commands = {
            "env", "podman", "neo4j", "format", "lint", "typecheck", "test", "e2e",
            "build", "fast-build", "refresh", "create-build", "release-build", 
            "clean", "build-status", "create-pr", "commit-data-changes", 
            "cleanup-branches", "shutdown-all", "status", "cache-status", 
            "verify-env", "check-integrity"
        }
        
        completion_commands_set = set(completion_commands)
        
        # Check that all expected commands are in completion
        missing_in_completion = expected_commands - completion_commands_set
        if missing_in_completion:
            self.fail(f"Commands missing from completion script: {missing_in_completion}")
        
        # Report extra commands (might be legacy aliases, which is okay)
        extra_in_completion = completion_commands_set - expected_commands
        if extra_in_completion:
            print(f"Extra commands in completion (possibly aliases): {extra_in_completion}")

    def test_scope_validation(self):
        """Test that scope arguments are properly validated"""
        # Test valid scopes
        valid_scopes = ["f2", "m7", "n100", "v3k"]
        
        for scope in valid_scopes:
            with self.subTest(scope=scope, command="refresh"):
                with patch.dict(os.environ, {"PATH": "/mock/path"}):
                    result = self.run_p3_command(["refresh", scope])
                    # Should not fail due to invalid scope
                    if result.returncode != 0 and "Invalid scope" in result.stderr:
                        self.fail(f"Valid scope {scope} was rejected")

    def test_p3_script_permissions(self):
        """Test that p3 script has correct permissions"""
        self.assertTrue(os.access(self.p3_script, os.X_OK), "p3 script should be executable")
        self.assertTrue(os.access(self.p3_script, os.R_OK), "p3 script should be readable")

    def test_p3_script_shebang(self):
        """Test that p3 script has proper shebang"""
        with open(self.p3_script, 'r') as f:
            first_line = f.readline().strip()
        
        # Should be shell script with proper shebang
        self.assertTrue(first_line.startswith("#!/"), "p3 script should have shebang")
        self.assertIn("sh", first_line, "p3 script should be shell script")


if __name__ == "__main__":
    import unittest
    unittest.main()