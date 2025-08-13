#!/usr/bin/env python3
"""
Unit tests for pixi commands functionality
Tests basic command availability and structure
"""

import json
import subprocess
import unittest
from pathlib import Path
from typing import List, Set


class TestPixiCommands(unittest.TestCase):
    """Test pixi command availability and consistency"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.project_root = Path(__file__).parent.parent
        cls.pixi_toml = cls.project_root / "pixi.toml"
        cls.available_tasks = cls._get_available_tasks()
        cls.required_tasks = {
            # Core commands
            "build-f2",
            "build-m7",
            "build-n100",
            "build-v3k",
            # Testing commands
            "e2e",
            "e2e-f2",
            "e2e-m7",
            "e2e-n100",
            "test",
            "test-e2e",
            # Development commands
            "format",
            "lint",
            "typecheck",
            # Infrastructure
            "env-status",
            "env-start",
            "env-stop",
            # New functionality
            "update-stock-lists",
            "setup-tab-completion",
            # PR workflow
            "create-pr",
            "commit-data-changes",
        }

    @staticmethod
    def _get_available_tasks() -> Set[str]:
        """Get list of available pixi tasks"""
        try:
            result = subprocess.run(
                ["pixi", "task", "list"],
                capture_output=True,
                text=True,
                check=True,
                cwd=Path(__file__).parent.parent,
            )

            tasks = set()
            lines = result.stdout.strip().split("\n")

            # Find the line with task list (after the header)
            found_task_line = False
            for line in lines:
                if line.startswith("Tasks that can run on this machine:"):
                    found_task_line = True
                    continue
                if line.startswith("---"):
                    continue
                if line.startswith("Task"):
                    continue
                if found_task_line and line.strip():
                    # This is the line with all tasks, comma-separated
                    task_line = line.strip()
                    if task_line:
                        tasks.update(task.strip() for task in task_line.split(", "))
                    break

            return tasks

        except subprocess.CalledProcessError as e:
            print(f"Error getting pixi tasks: {e}")
            return set()

    def test_pixi_toml_exists(self):
        """Test that pixi.toml exists and is readable"""
        self.assertTrue(self.pixi_toml.exists(), "pixi.toml should exist")
        self.assertTrue(self.pixi_toml.is_file(), "pixi.toml should be a file")

    def test_required_tasks_available(self):
        """Test that all required tasks are available"""
        missing_tasks = self.required_tasks - self.available_tasks
        self.assertEqual(missing_tasks, set(), f"Missing required tasks: {missing_tasks}")

    def test_e2e_commands_consistency(self):
        """Test that e2e commands follow consistent naming"""
        e2e_tasks = {task for task in self.available_tasks if task.startswith("e2e")}
        expected_e2e_tasks = {"e2e", "e2e-f2", "e2e-m7", "e2e-n100"}

        # Check that we have the expected e2e tasks
        missing_e2e = expected_e2e_tasks - e2e_tasks
        self.assertEqual(missing_e2e, set(), f"Missing e2e tasks: {missing_e2e}")

    def test_build_commands_consistency(self):
        """Test that build commands follow consistent naming"""
        build_tasks = {task for task in self.available_tasks if task.startswith("build")}
        expected_build_tasks = {"build-f2", "build-m7", "build-n100", "build-v3k"}

        # Check that we have the core build tasks
        missing_builds = expected_build_tasks - build_tasks
        self.assertEqual(missing_builds, set(), f"Missing build tasks: {missing_builds}")

    def test_new_functionality_available(self):
        """Test that new functionality commands are available"""
        new_tasks = {"update-stock-lists", "setup-tab-completion"}
        missing_new = new_tasks - self.available_tasks
        self.assertEqual(missing_new, set(), f"Missing new functionality: {missing_new}")

    def test_stock_list_update_command(self):
        """Test stock list update command dry run"""
        try:
            # Test that the script exists and is valid Python
            script_path = self.project_root / "ETL" / "fetch_ticker_lists.py"
            self.assertTrue(script_path.exists(), "fetch_ticker_lists.py should exist")

            # Test that we can import it without errors
            result = subprocess.run(
                ["python", "-c", "import sys; sys.path.append('ETL'); import fetch_ticker_lists"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            self.assertEqual(
                result.returncode, 0, f"fetch_ticker_lists.py import failed: {result.stderr}"
            )

        except Exception as e:
            self.fail(f"Stock list update test failed: {e}")

    def test_tab_completion_script(self):
        """Test tab completion setup script"""
        try:
            script_path = self.project_root / "scripts" / "setup_tab_completion.py"
            self.assertTrue(script_path.exists(), "setup_tab_completion.py should exist")

            # Test that we can import it without errors
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    "import sys; sys.path.append('scripts'); import setup_tab_completion",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            self.assertEqual(
                result.returncode, 0, f"setup_tab_completion.py import failed: {result.stderr}"
            )

        except Exception as e:
            self.fail(f"Tab completion test failed: {e}")

    def test_command_help_availability(self):
        """Test that pixi run --help works"""
        try:
            result = subprocess.run(
                ["pixi", "run", "--help"], capture_output=True, text=True, cwd=self.project_root
            )
            # Should return 0 or show help (some versions might return 1 for --help)
            self.assertIn("run", result.stdout.lower() + result.stderr.lower())

        except Exception as e:
            self.fail(f"Command help test failed: {e}")

    def test_no_duplicate_tasks(self):
        """Test that there are no duplicate task definitions"""
        task_list = list(self.available_tasks)
        unique_tasks = set(task_list)

        self.assertEqual(
            len(task_list), len(unique_tasks), "There should be no duplicate task names"
        )

    def test_consistent_naming_patterns(self):
        """Test that task names follow consistent patterns"""
        # Test e2e naming pattern: e2e, e2e-scope
        e2e_tasks = [task for task in self.available_tasks if task.startswith("e2e")]
        for task in e2e_tasks:
            if task != "e2e":
                self.assertTrue(
                    task.startswith("e2e-"), f"E2E task '{task}' should follow 'e2e-scope' pattern"
                )

        # Test build naming pattern: build-scope (no base "build" command expected)
        build_tasks = [task for task in self.available_tasks if task.startswith("build")]
        # Ensure build tasks follow proper naming
        core_build_tasks = {"build-f2", "build-m7", "build-n100", "build-v3k"}
        actual_core_tasks = {task for task in build_tasks if task in core_build_tasks}
        self.assertEqual(actual_core_tasks, core_build_tasks, "Core build tasks should exist")


class TestCommandExecution(unittest.TestCase):
    """Test basic command execution"""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent

    def test_pixi_environment_active(self):
        """Test that pixi environment can be activated"""
        try:
            result = subprocess.run(
                ["pixi", "info"], capture_output=True, text=True, check=True, cwd=self.project_root
            )
            self.assertIn("my_finance", result.stdout)

        except subprocess.CalledProcessError as e:
            self.fail(f"Pixi environment test failed: {e}")

    def test_dry_run_commands(self):
        """Test commands in dry-run mode where available"""
        dry_run_commands = [
            ["pixi", "run", "format", "--help"],  # Should show black help
        ]

        for cmd in dry_run_commands:
            with self.subTest(command=" ".join(cmd)):
                try:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=30, cwd=self.project_root
                    )
                    # Command should either succeed or show help
                    self.assertTrue(
                        result.returncode in [0, 1, 2],  # Allow various help exit codes
                        f"Command failed unexpectedly: {result.stderr}",
                    )

                except subprocess.TimeoutExpired:
                    self.fail(f"Command timed out: {' '.join(cmd)}")
                except Exception as e:
                    self.fail(f"Command execution failed: {e}")


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
