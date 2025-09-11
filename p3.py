#!/usr/bin/env python3
"""
P3 CLI - Simplified Workflow-Oriented Command System
Only 9 essential workflow commands for developer productivity
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
    return "1.0.34-environment-isolation-fix"


class P3CLI:
    """Simplified P3 CLI with only 9 workflow commands."""

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
        """Load the enhanced workflow commands."""
        return {
            # Core Workflow Commands (9 total)
            "ready": "python infra/system/workflow_ready.py",  # Start working
            "stop": "python infra/system/workflow_stop.py",  # Stop working (release resources)
            "reset": "python infra/system/workflow_reset.py",  # Fix environment
            "check": "python infra/development/workflow_check.py",  # Validate code
            "test": "python infra/run_test.py",  # Test
            "ship": "python infra/workflows/pr_creation.py",  # Create PR
            "debug": "python scripts/workflow/debug.py",  # Diagnose issues
            "build": "python ETL/build_dataset.py",  # Build dataset
            "version": "version_command",  # Version info
        }

    def _ensure_pixi_env(self):
        """Ensure pixi environment is properly set up"""
        pixi_python = self.project_root / ".pixi/envs/default/bin/python"
        if not pixi_python.exists():
            print("🔧 Pixi environment not found, installing...")
            result = subprocess.run(
                ["pixi", "install"], cwd=self.project_root, capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"❌ Failed to install pixi environment: {result.stderr}")
                return False
        return True

    def _execute_with_pixi_env(self, cmd_string: str) -> int:
        """Execute command with proper pixi environment isolation"""
        # Ensure we're in the right directory
        os.chdir(self.project_root)

        # Ensure pixi environment exists
        if not self._ensure_pixi_env():
            print("❌ Cannot proceed without proper pixi environment")
            return 1

        # For worktree environments, enhance environment variables
        env = os.environ.copy()
        if "worktree" in str(self.project_root):
            pixi_python = self.project_root / ".pixi/envs/default/bin/python"
            pixi_site_packages = (
                self.project_root / ".pixi/envs/default/lib/python3.12/site-packages"
            )

            if pixi_python.exists():
                env["PYTHON"] = str(pixi_python)
                env["PYTHONEXECUTABLE"] = str(pixi_python)

            if pixi_site_packages.exists():
                # Ensure Python path includes pixi site-packages
                pythonpath = env.get("PYTHONPATH", "")
                pixi_path = str(pixi_site_packages)
                if pixi_path not in pythonpath:
                    env["PYTHONPATH"] = f"{pixi_path}:{pythonpath}" if pythonpath else pixi_path

        print(f"🚀 Executing: {cmd_string}")
        print(f"   Working directory: {self.project_root}")

        # Execute with enhanced environment
        result = subprocess.run(cmd_string, shell=True, env=env, cwd=self.project_root)
        return result.returncode

    def run(self, command: str, args: list):
        """Execute a P3 command."""
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

        # Build command strings with proper pixi integration
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

        # Execute command with proper environment isolation
        returncode = self._execute_with_pixi_env(cmd_string)
        sys.exit(returncode)

    def print_help(self):
        """Print help message."""
        print(
            """
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

DATA & VERSION (3 commands):
  p3 build [scope]          Build dataset (f2/m7/n100/v3k)
  p3 version [level]        Show/increment version

STOP OPTIONS:
  --full                    Stop Podman machine (complete shutdown)
  --force                   Force stop without graceful shutdown

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
    # Ensure worktree Python isolation with multiple fallback strategies
    isolation_attempted = False

    # Strategy 1: Try infra.system import
    try:
        from infra.system.worktree_isolation import WorktreeIsolationManager

        manager = WorktreeIsolationManager()
        if manager.auto_switch_python():
            isolation_attempted = True
    except (ImportError, ModuleNotFoundError):
        pass

    # Strategy 2: Try scripts import if infra import failed
    if not isolation_attempted:
        try:
            # Add current directory to Python path
            current_dir = Path(__file__).parent
            if str(current_dir) not in sys.path:
                sys.path.insert(0, str(current_dir))

            from scripts.worktree_isolation import WorktreeIsolationManager

            manager = WorktreeIsolationManager()
            if manager.auto_switch_python():
                isolation_attempted = True
        except (ImportError, ModuleNotFoundError):
            pass

    # Strategy 3: Direct path-based detection and switching
    if not isolation_attempted:
        try:
            current_path = Path(__file__).parent
            if "worktree" in str(current_path):
                pixi_python = current_path / ".pixi/envs/default/bin/python"
                if pixi_python.exists():
                    current_python = Path(sys.executable).resolve()
                    if current_python != pixi_python.resolve():
                        print(f"🔄 P3 switching to worktree Python: {pixi_python}")
                        os.execv(str(pixi_python), [str(pixi_python)] + sys.argv)
        except Exception as e:
            print(f"⚠️  P3 Python isolation warning: {e}")
            print("   Continuing with current Python environment...")

    cli = P3CLI()
    command = sys.argv[1] if len(sys.argv) > 1 else None
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    cli.run(command, args)


if __name__ == "__main__":
    main()
