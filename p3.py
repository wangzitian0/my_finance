#!/usr/bin/env python3
"""
P3 CLI - Simplified Workflow-Oriented Command System
Only 9 essential workflow commands for developer productivity
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional


def get_version_string():
    return "2.0.1-simplified"


class P3CLI:
    """Simplified P3 CLI with only 9 workflow commands."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.commands = self._load_commands()

    def _get_current_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"

    def _load_commands(self) -> Dict[str, str]:
        """Load the essential workflow commands."""
        return {
            # Core Workflow Commands (9 total)
            "ready": "python infra/system/workflow_ready.py",  # Start working
            "stop": "python infra/system/workflow_stop.py",  # Stop working (release resources)
            "reset": "python infra/system/workflow_reset.py",  # Fix environment
            "check": "python infra/development/workflow_check.py",  # Validate code
            "test": "python scripts/utilities/run_test.py",  # Test
            "ship": "python infra/workflows/pr_creation.py",  # Create PR
            "debug": "python scripts/workflow/debug.py",  # Diagnose issues
            "build": "python ETL/build_dataset.py",  # Build dataset
            "version": "version_command",  # Version info
        }

    def run(self, command: str, args: list):
        """Execute a P3 command."""
        start_time = time.time()
        print(f"🚀 P3 CLI v{get_version_string()} - Command: {command}")
        print(f"⏰ Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        if command == "help" or command is None:
            self.print_help()
            return

        if command not in self.commands:
            print(f"❌ Unknown command: {command}")
            print(
                "Available commands: ready, stop, reset, check, test, ship, debug, build, version"
            )
            print("Use 'p3 help' for details")
            sys.exit(1)

        # Handle version command
        if command == "version":
            print(f"P3 Version: {get_version_string()}")
            print(f"   Script: {Path(__file__).resolve()}")
            print(f"   Working directory: {self.project_root}")
            print(f"   Git branch: {self._get_current_branch()}")
            return

        # Handle ship command with special arguments
        if command == "ship":
            if len(args) < 2:
                print("❌ Error: title and issue number required")
                print('Usage: p3 ship "PR Title" ISSUE_NUMBER')
                sys.exit(1)
            cmd_string = f'pixi run {self.commands[command]} "{args[0]}" {args[1]}'
        elif command in ["build", "test", "check"]:
            scope = args[0] if args else "f2"
            cmd_string = f"pixi run {self.commands[command]} {scope}"
            print(f"📋 Using scope: {scope}")
        else:
            cmd_string = f"pixi run {self.commands[command]}"
            if args:
                cmd_string += " " + " ".join(args)

        # Execute command with detailed logging
        print(f"🔧 Command: {self.commands[command]}")
        print(f"🚀 Executing: {cmd_string}")
        print(f"📁 Working directory: {self.project_root}")
        print(f"🌿 Git branch: {self._get_current_branch()}")
        print("=" * 50)

        os.chdir(self.project_root)

        # Log execution start
        exec_start = time.time()
        print(f"⚡ Command execution started at {time.strftime('%H:%M:%S')}")

        result = subprocess.run(cmd_string, shell=True)

        # Log execution completion
        exec_end = time.time()
        exec_duration = exec_end - exec_start
        total_duration = exec_end - start_time

        print("=" * 50)
        print(f"⏱️  Command execution time: {exec_duration:.2f}s")
        print(f"⏱️  Total P3 time: {total_duration:.2f}s")
        print(f"🏁 Finished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔄 Exit code: {result.returncode}")

        sys.exit(result.returncode)

    def print_help(self):
        """Print help message."""
        print(
            f"""
🚀 P3 CLI - Workflow-Oriented Development Commands

DAILY WORKFLOW (5 commands):
  p3 ready                  Start working (env + services)
  p3 stop [--full] [--force] Stop working (release resources)
  p3 check [scope]          Validate code (format + lint + basic tests)
  p3 test [scope]           Unit tests + integration + e2e (superset of CI)
  p3 ship "title" issue     Publish work (comprehensive test + PR + cleanup)

TROUBLESHOOTING (2 commands):
  p3 debug                  Diagnose issues (status check)
  p3 reset                  Fix environment (clean restart)

DATA & VERSION (2 commands):
  p3 build [scope]          Build dataset (f2/m7/n100/v3k)
  p3 version                Show version

STOP OPTIONS:
  --full                    Stop Podman machine (complete shutdown)
  --force                   Force stop without graceful shutdown

SCOPES:
  f2    Fast 2 companies (development)
  m7    Magnificent 7 (testing)
  n100  NASDAQ 100 (validation)  
  v3k   Russell 3000 (production)

Version: {get_version_string()}
"""
        )


def main():
    """Main entry point."""
    cli = P3CLI()
    command = sys.argv[1] if len(sys.argv) > 1 else None
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    cli.run(command, args)


if __name__ == "__main__":
    main()
