#!/usr/bin/env python3
"""
P3 CLI - Simplified Workflow-Oriented Command System
Only 9 essential workflow commands for developer productivity

SSOT I/O Integration: Uses common.core.directory_manager for all file operations
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional

# SSOT I/O Enforcement: Import directory_manager for centralized path management
try:
    from common.core.directory_manager import DirectoryManager
    SSOT_AVAILABLE = True
except ImportError as e:
    # Fallback for development environments where common module may not be available
    DirectoryManager = None
    SSOT_AVAILABLE = False
    import logging
    logging.warning(f"DirectoryManager not available, using fallback: {e}")


def get_version_string():
    return "2.0.1-simplified"


class P3CLI:
    """Simplified P3 CLI with only 9 workflow commands.

    SSOT I/O Integration: Uses DirectoryManager for all path operations
    """

    def __init__(self):
        # SSOT I/O Enforcement: Use DirectoryManager for project root detection
        if DirectoryManager:
            self.directory_manager = DirectoryManager()
            self.project_root = self.directory_manager.root_path
            self._log_ssot_status("DirectoryManager initialized successfully")
        else:
            # Fallback for environments without directory_manager
            self.project_root = Path.cwd()
            self._log_ssot_status("Using fallback mode - DirectoryManager not available")

        self.commands = self._load_commands()

    def _log_ssot_status(self, message: str):
        """Log SSOT integration status for debugging."""
        # Only log in debug mode to avoid cluttering normal output
        if os.environ.get('P3_DEBUG'):
            print(f"🔧 SSOT: {message}")

    def _get_current_branch(self) -> str:
        """Get current git branch using SSOT subprocess execution."""
        try:
            # SSOT I/O Enforcement: Use directory_manager's secure subprocess execution
            if hasattr(self, 'directory_manager') and self.directory_manager:
                result = self.directory_manager._secure_subprocess_run(
                    ["git", "branch", "--show-current"], timeout=5
                )
                return result.stdout.strip() if result.returncode == 0 else "unknown"
            else:
                # Fallback for environments without directory_manager
                import subprocess
                result = subprocess.run(
                    ["git", "branch", "--show-current"], capture_output=True, text=True, timeout=5
                )
                return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "unknown"

    def _load_commands(self) -> Dict[str, str]:
        """Load the essential workflow commands.

        Each command maps to a specific script that handles the workflow logic.
        Commands are organized by functionality:
        - Workflow: ready, stop, reset (environment management)
        - Quality: check, test (code validation)
        - Publishing: ship (PR creation)
        - Data: build (dataset generation)
        - Info: version (system information)

        All commands use SSOT I/O patterns through directory_manager integration.
        """
        return {
            # Core Workflow Commands (8 total)
            "ready": "python infra/system/workflow_ready.py",  # Start working - environment setup
            "stop": "python infra/system/workflow_stop.py",   # Stop working - resource cleanup
            "reset": "python infra/system/workflow_reset.py", # Fix environment - nuclear reset
            "check": "python infra/development/workflow_check.py",  # Validate code - format, lint, tests
            "test": "python scripts/utilities/run_test.py",   # Test - comprehensive testing
            "ship": "python infra/workflows/pr_creation.py", # Create PR - publish workflow
            "build": "python ETL/build_dataset.py",          # Build dataset - data generation
            "version": "version_command",                     # Version info - system details
        }

    def run(self, command: str, args: list):
        """Execute a P3 command with comprehensive logging and error handling.

        This method implements the P3 CLI delegation pattern:
        1. Command validation and routing
        2. Argument processing and scope handling
        3. SSOT I/O enforcement through directory_manager
        4. Comprehensive execution logging
        5. Error handling and diagnostics

        Args:
            command: P3 command to execute (ready, test, ship, etc.)
            args: Command arguments (scope, title, issue number, etc.)

        The method uses directory_manager for secure subprocess execution
        where possible, falling back to shell execution for complex pixi commands.
        """
        start_time = time.time()
        print(f"🚀 P3 CLI v{get_version_string()} - Command: {command}")
        print(f"⏰ Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        if command == "help" or command is None:
            self.print_help()
            return

        if command not in self.commands:
            print(f"❌ Unknown command: {command}")
            print("Available commands: ready, stop, reset, check, test, ship, build, version")
            print("Use 'p3 help' for details")
            sys.exit(1)

        # Handle version command
        if command == "version":
            print(f"P3 Version: {get_version_string()}")
            print(f"   Script: {Path(__file__).resolve()}")
            print(f"   Working directory: {self.project_root}")
            print(f"   Git branch: {self._get_current_branch()}")
            print(f"   SSOT I/O Integration: {'✅ Enabled' if SSOT_AVAILABLE else '⚠️  Fallback Mode'}")
            if hasattr(self, 'directory_manager') and self.directory_manager:
                print(f"   DirectoryManager: {type(self.directory_manager).__name__}")
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

        # SSOT I/O Enforcement: Use directory_manager's secure subprocess execution where possible
        try:
            if hasattr(self, 'directory_manager') and self.directory_manager and not cmd_string.startswith('pixi run'):
                # For simple commands, use secure execution
                cmd_args = cmd_string.split()
                result = self.directory_manager._secure_subprocess_run(cmd_args, timeout=3600)
            else:
                # For complex pixi commands, use shell execution (required for pixi run)
                import subprocess
                result = subprocess.run(cmd_string, shell=True)
        except Exception as e:
            print(f"⚠️  SSOT subprocess execution failed, falling back to shell: {e}")
            import subprocess
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

        # Provide helpful diagnostics for failures
        if result.returncode != 0:
            print()
            print("🔍 COMMAND FAILED - Quick Diagnostics:")
            print(f"   Command: {command}")
            print(f"   Exit code: {result.returncode}")
            print()
            print("💡 Common solutions:")
            if command == "ready":
                print("   • Check if Podman machine is running: podman machine list")
                print("   • Try: p3 reset (clean restart)")
                print("   • Check system resources: Activity Monitor")
            elif command == "test":
                print("   • Check if environment is ready: p3 ready")
                print("   • Try smaller scope: p3 test f2")
                print("   • Check dependencies: pixi install")
            elif command == "ship":
                print("   • Ensure tests pass first: p3 test f2")
                print("   • Check git status and commit changes")
                print("   • Verify issue number is correct")
            elif command == "check":
                print("   • Check code formatting issues")
                print("   • Try fixing with: p3 ready")
                print("   • Check pixi environment: pixi install")
            else:
                print("   • Try: p3 ready (setup environment)")
                print("   • Check logs above for specific errors")
                print("   • Use 'p3 reset' for major issues")

        sys.exit(result.returncode)

    def print_help(self):
        """Print help message with SSOT integration information."""
        ssot_status = "✅ SSOT I/O Enabled" if SSOT_AVAILABLE else "⚠️  SSOT I/O Fallback"

        print(
            f"""
🚀 P3 CLI - Workflow-Oriented Development Commands

DAILY WORKFLOW (5 commands):
  p3 ready                  Start working (env + services)
  p3 stop [--full] [--force] Stop working (release resources)
  p3 check [scope]          Validate code (format + lint + basic tests)
  p3 test [scope]           Unit tests + integration + e2e (superset of CI)
  p3 ship "title" issue     Publish work (comprehensive test + PR + cleanup)

TROUBLESHOOTING (1 command):
  p3 reset                  Fix environment (clean restart)

DATA & VERSION (2 commands):
  p3 build [scope]          Build dataset (f2/m7/n100/v3k)
  p3 version                Show version and system status

STOP OPTIONS:
  --full                    Stop Podman machine (complete shutdown)
  --force                   Force stop without graceful shutdown

SCOPES:
  f2    Fast 2 companies (development)
  m7    Magnificent 7 (testing)
  n100  NASDAQ 100 (validation)
  v3k   Russell 3000 (production)

SYSTEM:
  Version: {get_version_string()}
  SSOT I/O: {ssot_status}
  Location: {Path(__file__).resolve()}

DELEGATION PATTERN:
  Root p3.py → infra/p3/p3.py (modular L1/L2 architecture)
  All file operations use DirectoryManager for SSOT enforcement
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
