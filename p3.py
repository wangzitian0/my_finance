#!/usr/bin/env python3
"""
P3 CLI - Simplified Workflow-Oriented Command System
Only 8 essential workflow commands for developer productivity
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

# Import version management - Updated for infra/p3/ migration
try:
    from infra.p3.p3_version_simple import get_version_string, increment_version

    VERSION_ENABLED = True
except ImportError:
    VERSION_ENABLED = False


def get_version_string():
    return "1.0.33-worktree-fix"


class P3CLI:
    """Simplified P3 CLI with only 8 workflow commands."""

    def __init__(self):
        self.project_root = self._find_project_root()
        self.commands = self._load_commands()

    def _find_project_root(self) -> Path:
        """Find project root (handle worktrees)."""
        current_path = Path(__file__).parent

        # In worktree, stay in current directory
        if "worktree" in str(current_path):
            return current_path

        # Find main project directory
        while current_path != current_path.parent:
            if (current_path / "pixi.toml").exists():
                return current_path
            current_path = current_path.parent

        return Path(__file__).parent

    def _load_commands(self) -> Dict[str, str]:
        """Load the 8 workflow commands."""
        return {
            # Core Workflow Commands (8 total)
            "ready": "python scripts/workflow/ready.py",  # Start working
            "reset": "python scripts/workflow/reset.py",  # Fix environment
            "check": "python scripts/workflow/check.py",  # Validate code
            "test": "python infra/run_test.py",  # Test
            "ship": "python infra/workflows/pr_creation.py",  # Create PR
            "debug": "python scripts/workflow/debug.py",  # Diagnose issues
            "build": "python ETL/build_dataset.py",  # Build dataset
            "version": "version_command",  # Version info
        }

    def run(self, command: str, args: list):
        """Execute a P3 command."""
        if command == "help" or command is None:
            self.print_help()
            return

        if command not in self.commands:
            print(f"❌ Unknown command: {command}")
            print("Available commands: ready, reset, check, test, ship, debug, build, version")
            print("Use 'p3 help' for details")
            sys.exit(1)

        # Handle special commands
        if command == "version":
            if VERSION_ENABLED:
                if args and args[0] in ["major", "minor", "patch"]:
                    new_version = increment_version(args[0])
                    print(f"Version: {new_version}")
                else:
                    print(f"P3 Version: {get_version_string()}")
            else:
                print("Version information not available")
            return

        if command == "ship":
            if len(args) < 2:
                print("❌ Error: title and issue number required")
                print('Usage: p3 ship "PR Title" ISSUE_NUMBER')
                sys.exit(1)
            cmd_string = f'pixi run {self.commands[command]} "{args[0]}" {args[1]}'
        elif command == "build":
            scope = args[0] if args else "f2"
            cmd_string = f"pixi run {self.commands[command]} {scope}"
        elif command == "test":
            scope = args[0] if args else "f2"
            cmd_string = f"pixi run {self.commands[command]} {scope}"
        elif command == "check":
            scope = args[0] if args else "f2"
            cmd_string = f"pixi run {self.commands[command]} {scope}"
        else:
            cmd_string = f"pixi run {self.commands[command]}"
            if args:
                cmd_string += " " + " ".join(args)

        # Execute command
        print(f"🚀 Executing: {cmd_string}")
        os.chdir(self.project_root)
        result = subprocess.run(cmd_string, shell=True)
        sys.exit(result.returncode)

    def print_help(self):
        """Print help message."""
        print(
            """
🚀 P3 CLI - Workflow-Oriented Development Commands

DAILY WORKFLOW (4 commands):
  p3 ready                  Start working (env + services)
  p3 check [scope]          Validate code (format + lint + test)
  p3 test [scope]           Comprehensive testing (e2e validation)
  p3 ship "title" issue     Publish work (test + PR + cleanup)

TROUBLESHOOTING (2 commands):
  p3 debug                  Diagnose issues (status check)
  p3 reset                  Fix environment (clean restart)

DATA & VERSION (2 commands):
  p3 build [scope]          Build dataset (f2/m7/n100/v3k)
  p3 version [level]        Show/increment version

SCOPES:
  f2    Fast 2 companies (development)
  m7    Magnificent 7 (testing)
  n100  NASDAQ 100 (validation)
  v3k   Russell 3000 (production)

Version: {version}
""".format(
                version=get_version_string() if VERSION_ENABLED else "unknown"
            )
        )


def main():
    """Main entry point."""
    # Ensure worktree Python isolation
    try:
        from infra.system.worktree_isolation import WorktreeIsolationManager

        manager = WorktreeIsolationManager()
        manager.auto_switch_python()
    except ImportError:
        pass  # Fallback to current Python

    cli = P3CLI()
    command = sys.argv[1] if len(sys.argv) > 1 else None
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    cli.run(command, args)


if __name__ == "__main__":
    main()
