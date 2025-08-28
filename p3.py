#!/usr/bin/env python3
"""
Unified p3 CLI for my_finance project
Centralizes all development commands under one consistent interface

This replaces the shell-based p3 script with a proper Python CLI system
as specified in Issue #111.

Enhanced with Agent Execution Monitoring System (Issue #180).
"""
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Import execution monitoring
try:
    from common.execution_monitor import ExecutionResult, get_monitor

    MONITORING_ENABLED = True
except ImportError:
    MONITORING_ENABLED = False
    print("⚠️  Execution monitoring not available")


class P3CLI:
    """Unified p3 CLI system for my_finance project."""

    def __init__(self):
        # Find the actual project root (handle worktrees)
        current_path = Path(__file__).parent

        # CRITICAL FIX: In worktrees, stay in current directory for git operations
        # The pixi.toml should be accessible from worktree via symlinks or relative paths
        if "worktree" in str(current_path):
            # Stay in the worktree directory for proper git context
            self.project_root = current_path

            # Verify we can access pixi.toml (should be available via symlink or relative path)
            parts = current_path.parts
            try:
                # Find the main project directory for pixi.toml reference only
                git_index = parts.index(".git")
                main_project = Path(*parts[:git_index])
                if (
                    not (current_path / "pixi.toml").exists()
                    and (main_project / "pixi.toml").exists()
                ):
                    # Note: We stay in worktree but know where pixi.toml is
                    print(f"📍 Worktree detected: staying in {current_path}")
                    print(f"📁 Pixi config referenced from: {main_project}")
            except ValueError:
                pass
        else:
            # Look for the main project directory (contains pixi.toml)
            while current_path != current_path.parent:
                if (current_path / "pixi.toml").exists():
                    self.project_root = current_path
                    break
                current_path = current_path.parent
            else:
                self.project_root = Path(__file__).parent

        self.commands = self._load_command_mapping()

    def _sanitize_python_command(self, cmd_string: str) -> str:
        """
        Sanitize pixi python -c commands to prevent syntax errors.

        This addresses Issue #153: malformed pixi commands with unquoted parameters.
        """
        if "pixi run python -c" not in cmd_string:
            return cmd_string

        # Extract the python code portion - handle mixed quote scenarios correctly
        if 'pixi run python -c "' in cmd_string:
            # Double quote style (outer quotes are double)
            start = cmd_string.find('pixi run python -c "') + len('pixi run python -c "')
            end = cmd_string.rfind('"')
            python_code = cmd_string[start:end]
        elif "pixi run python -c '" in cmd_string:
            # Single quote style (outer quotes are single)
            start = cmd_string.find("pixi run python -c '") + len("pixi run python -c '")
            end = cmd_string.rfind("'")
            python_code = cmd_string[start:end]
        else:
            return cmd_string

        # Check for common parameter quote issues
        issues_found = False
        fixed_code = python_code

        # Fix unquoted string parameters in common patterns
        import re

        # Pattern: function_call(unquoted_string, [unquoted_list], unquoted_string)
        patterns_to_fix = [
            # Handle build_runtime_config with unquoted parameters
            (
                r'build_runtime_config\(([^,\'"()]+),\s*\[([^,\'"()]+)\],\s*([^,\'"()]+)\)',
                r"build_runtime_config('\1', ['\2'], '\3')",
            ),
            # More general case for function parameters
            (
                r'(\w+)\(([^,\'"()]+),\s*\[([^,\'"()]+)\],\s*([^,\'"()]+)\)',
                r"\1('\2', ['\3'], '\4')",
            ),
        ]

        for pattern, replacement in patterns_to_fix:
            if re.search(pattern, fixed_code):
                fixed_code = re.sub(pattern, replacement, fixed_code)
                issues_found = True

        if issues_found:
            # Reconstruct the command with fixed code
            if '"' in cmd_string and 'pixi run python -c "' in cmd_string:
                # Double-quoted command
                prefix = 'pixi run python -c "'
                suffix = '"'
                # Escape double quotes in the fixed code
                escaped_fixed_code = fixed_code.replace('"', '\\"')
            else:
                # Single-quoted command
                prefix = "pixi run python -c '"
                suffix = "'"
                # Escape single quotes in the fixed code
                escaped_fixed_code = fixed_code.replace("'", "\\'")

            fixed_cmd = prefix + escaped_fixed_code + suffix

            print(f"⚠️  Fixed malformed pixi command (Issue #153)")
            print(f"   Original: {cmd_string}")
            print(f"   Fixed:    {fixed_cmd}")

            return fixed_cmd

        return cmd_string

    def _validate_command_syntax(self, cmd_string: str) -> str:
        """
        Validate and fix command syntax before execution.

        This is the main fix for Issue #153: malformed pixi commands.
        """
        # Apply sanitization for Python commands
        sanitized = self._sanitize_python_command(cmd_string)

        # Additional validation could go here

        return sanitized

    def _load_command_mapping(self) -> Dict[str, str]:
        """Load command mappings from configuration."""
        return {
            # Environment Management (p3 calls ansible for infra, pixi for Python)
            "activate": "pixi shell",
            "env-setup": "ansible-playbook infra/ansible/setup.yml",
            "env-start": "ansible-playbook infra/ansible/start.yml",
            "env-stop": "ansible-playbook infra/ansible/stop.yml",
            "env-status": "pixi run python infra/comprehensive_env_status.py",
            "env-reset": "ansible-playbook infra/ansible/reset.yml",
            # Development Commands (p3 calls pixi to manage Python execution)
            "format": "pixi run python -m black --line-length 100 . && pixi run python -m isort .",
            "lint": "pixi run python -m pylint ETL dcf_engine common graph_rag --disable=C0114,C0115,C0116,R0903,W0613",
            "typecheck": "pixi run python -m mypy ETL dcf_engine common graph_rag --ignore-missing-imports",
            "test": "pixi run python -m pytest tests/ -v --cov=ETL --cov=dcf_engine --cov-report=html",
            # Build Commands (p3 calls pixi for Python execution)
            "build": "pixi run python ETL/build_dataset.py {scope}",
            "fast-build": "pixi run python ETL/build_dataset.py {scope} --fast-mode",
            "refresh": "pixi run python ETL/build_dataset.py {scope}",  # Alias for build
            # Data Management (p3 calls pixi for Python execution)
            "create-build": "pixi run python scripts/manage_build_data.py create",
            "release-build": "pixi run python scripts/manage_build_data.py release",
            "commit-data-changes": "pixi run python infra/commit_data_changes.py",
            "build-status": "pixi run python -c 'from common.build_tracker import BuildTracker; bt=BuildTracker.get_latest_build(); print(bt.get_build_status() if bt else \"No builds found\")'",
            "clean": 'pixi run python -c \'import shutil; from pathlib import Path; from common import get_data_path, DataLayer; build_dir = Path(get_data_path(DataLayer.QUERY_RESULTS)); [shutil.rmtree(d) for d in build_dir.glob("build_*") if d.is_dir()]; print("🧹 Cleaned")\'',
            # PR and Git Workflow (p3 calls pixi for Python execution)
            "create-pr": "pixi run python infra/create_pr_with_test.py {title} {issue}",
            "cleanup-branches": "pixi run python infra/cleanup_merged_branches.py",
            "e2e": "pixi run python infra/create_pr_with_test.py --skip-pr-creation",
            # Analysis and Reporting (p3 calls pixi for Python execution)
            "dcf-analysis": "pixi run python dcf_engine/pure_llm_dcf.py",
            "dcf-report": "pixi run python dcf_engine/pure_llm_dcf.py",
            "generate-report": "pixi run python dcf_engine/pure_llm_dcf.py",
            "validate-strategy": "pixi run python ETL/manage.py validate",
            # Infrastructure Management (direct system commands, not Python)
            "podman-status": "podman ps -a --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'",
            "neo4j-logs": "podman logs neo4j-finance",
            "neo4j-connect": "podman exec -it neo4j-finance cypher-shell -u neo4j -p finance123",
            "neo4j-restart": "podman restart neo4j-finance",
            "neo4j-stop": "podman stop neo4j-finance",
            "neo4j-start": "podman start neo4j-finance",
            # Status and Validation (p3 calls pixi for Python execution)
            "status": "pixi run python infra/comprehensive_env_status.py",
            "cache-status": "pixi run python infra/show_cache_status.py",
            "verify-env": 'pixi run python -c \'import sys; print(f"Python: {sys.version}"); import torch, sklearn, sentence_transformers; print("✅ ML dependencies available"); import neomodel; print("✅ Neo4j ORM available")\'',
            "check-integrity": 'pixi run python -c \'from pathlib import Path; from common import get_data_path, DataLayer; dirs = [get_data_path(DataLayer.RAW_DATA), get_data_path(DataLayer.DAILY_DELTA), get_data_path(DataLayer.QUERY_RESULTS)]; [print(f"📁 {Path(d).name}: {"✅ exists" if Path(d).exists() else "❌ missing"}") for d in dirs]\'',
            "shutdown-all": "pixi run python infra/shutdown_all.py",
            # SEC Integration Commands (p3 calls pixi for Python execution)
            "test-sec-integration": "pixi run python dcf_engine/sec_integration_template.py",
            "test-sec-recall": "pixi run python dcf_engine/sec_recall_usage_example.py",
            "verify-sec-data": 'pixi run python -c \'from pathlib import Path; from collections import Counter; from common import get_source_path, DataLayer; sec_path = Path(get_source_path("sec-edgar", DataLayer.DAILY_DELTA)); sec_files = list(sec_path.rglob("*.txt")); print(f"📄 Found {len(sec_files)} total SEC documents"); ticker_counts = Counter(f.name.split("_")[0] for f in sec_files); print("📊 By ticker:"); [print(f"  - {ticker}: {count} files") for ticker, count in sorted(ticker_counts.items())]\'',
            "test-sec-config": "pixi run python -c \"from common.orthogonal_config import orthogonal_config; config = orthogonal_config.build_runtime_config('f2', ['sec_edgar'], 'development'); print('SEC Edgar Config:', config)\"",
            # ETL and Data Commands (p3 calls pixi for Python execution)
            "etl-status": "pixi run python ETL/manage.py status",
            "run-job": "pixi run python ETL/run_job.py",
            "build-schema": "pixi run python ETL/build_schema.py",
            "import-data": "pixi run python ETL/import_data.py",
            "check-coverage": "pixi run python ETL/check_coverage.py",
            "migrate-data": "pixi run python ETL/migrate_data_structure.py",
            # Additional Build Commands (p3 calls pixi for Python execution)
            "build-size": 'pixi run python -c \'from pathlib import Path; import subprocess; from common import get_data_path, DataLayer; build_path = get_data_path(DataLayer.QUERY_RESULTS); result = subprocess.run(["du", "-sh", build_path], capture_output=True, text=True); print(f"📦 Build directory size: {result.stdout.strip()}")\'',
            # Ollama and LLM Commands
            "build-sec-library": "pixi run python dcf_engine/sec_document_manager.py",
            "llm-dcf-report": "pixi run python dcf_engine/llm_dcf_generator.py --ticker AAPL",
            "hybrid-dcf-report": "pixi run python dcf_engine/legacy_testing/hybrid_dcf_analyzer.py",
            # Additional Analysis Commands
            "generate-report-legacy": "pixi run python dcf_engine/legacy_testing/generate_dcf_report.py",
            "backtest": "echo 'Backtest simulation completed (placeholder)' && pixi run python dcf_engine/legacy_testing/simple_m7_dcf.py",
            "test-semantic-retrieval": "pixi run python test_semantic_retrieval.py",
            # Git Hooks Management
            "install-hooks": f"pixi run python {self.project_root}/scripts/install_git_hooks.py",
            "check-hooks": f"pixi run python {self.project_root}/scripts/check_git_hooks.py",
            # Legacy DCF Commands
            "dcf-analysis-legacy": "pixi run python dcf_engine/legacy_testing/m7_dcf_analysis.py",
            "dcf-report-legacy": "pixi run python dcf_engine/legacy_testing/generate_dcf_report.py",
            "simple-dcf-legacy": "pixi run python dcf_engine/legacy_testing/simple_m7_dcf.py",
            "hybrid-dcf-legacy": "pixi run python dcf_engine/legacy_testing/hybrid_dcf_analyzer.py",
            # Testing Commands
            "test-yfinance": "pixi run python ETL/tests/integration/test_yfinance.py",
            "test-config": "pixi run python -m pytest ETL/tests/test_config.py -v",
            "test-dcf-report": "pixi run python -m pytest dcf_engine/test_dcf_report.py -v",
            # Monitoring Commands (Issue #180)
            "monitoring-summary": "pixi run python -c 'from common.monitoring_dashboard import print_monitoring_summary; print_monitoring_summary(7)'",
            "monitoring-report": "pixi run python -c 'from common.monitoring_dashboard import export_monitoring_report; print(f\"Report: {export_monitoring_report(7)}\")'",
            "monitoring-stats": "pixi run python -c 'from common.execution_monitor import get_monitor; import json; print(json.dumps(get_monitor().get_execution_stats(7), indent=2))'",
        }

    def _get_valid_scopes(self) -> List[str]:
        """Get list of valid scopes for build commands."""
        return ["f2", "m7", "n100", "v3k"]

    def _resolve_scope(self, scope: Optional[str]) -> str:
        """Resolve scope parameter, defaulting to m7."""
        if scope is None:
            return "m7"

        valid_scopes = self._get_valid_scopes()
        if scope not in valid_scopes:
            print(f"❌ Invalid scope: {scope}")
            print(f"Valid scopes: {', '.join(valid_scopes)}")
            sys.exit(1)

        return scope

    def _handle_scope_command(self, command: str, args: List[str]) -> str:
        """Handle commands that support scope parameters."""
        scope_commands = ["build", "fast-build", "refresh", "e2e"]

        if command in scope_commands:
            scope = args[0] if args else None
            resolved_scope = self._resolve_scope(scope)

            # Remove scope from args if it was provided
            remaining_args = args[1:] if args and args[0] in self._get_valid_scopes() else args

            if command == "e2e":
                # E2E command passes scope to create_pr_with_test.py for proper F2/M7 testing
                return f"pixi run python infra/create_pr_with_test.py --skip-pr-creation --scope {resolved_scope}"
            else:
                # Build commands use scope directly
                cmd_template = self.commands[command]
                return cmd_template.format(scope=resolved_scope)

        return self.commands[command]

    def _handle_special_commands(self, command: str, args: List[str]) -> Optional[str]:
        """Handle special commands that need custom logic."""

        if command == "activate":
            print("📦 Activating pixi environment...")
            print("Run: pixi shell")
            print("Note: This command needs to be run directly as 'pixi shell'")
            return None

        if command == "create-pr":
            if len(args) < 2:
                print("❌ Error: title and issue number are required")
                print('Usage: p3 create-pr "PR Title" ISSUE_NUMBER')
                sys.exit(1)

            title, issue = args[0], args[1]
            remaining_args = args[2:]
            cmd = f'pixi run python infra/create_pr_with_test.py "{title}" {issue}'
            if remaining_args:
                cmd += " " + " ".join(remaining_args)
            return cmd

        if command == "cleanup-branches":
            return "pixi run python infra/cleanup_merged_branches.py"

        if command == "test":
            cmd = "pixi run python -m pytest tests/ -v --cov=ETL --cov=dcf_engine --cov-report=html"
            if "--quick" in args:
                # Quick test mode - run basic structure test only
                cmd = "pixi run python -m pytest tests/test_basic_structure.py -v"
            elif "--protection" in args:
                # Directory structure protection tests
                cmd = "pixi run python tests/test_directory_structure_protection.py"
            return cmd

        return None

    def show_help(self):
        """Show comprehensive help information."""
        help_text = """
p3 - Unified developer commands (my_finance)

Usage:
  p3 <command> [args...]

Environment Management:
  activate               Activate pixi environment (use 'pixi shell' directly)
  env-setup              Initial environment setup (Podman, Neo4j)
  env-start              Start all services
  env-stop               Stop all services
  env-status             Check environment status
  env-reset              Reset everything (destructive)

Container Management:
  podman-status          Check container status
  neo4j-logs             View Neo4j logs
  neo4j-connect          Connect to Neo4j shell
  neo4j-restart          Restart Neo4j container
  neo4j-stop             Stop Neo4j container
  neo4j-start            Start Neo4j container

Development Commands:
  format                 Format code (black + isort)
  lint                   Lint code (pylint)
  typecheck              Type check with mypy
  test                   Run tests (pytest)
  test --quick           Run quick tests only
  test --protection      Run directory structure protection tests
  e2e [scope]            End-to-end validation (default: m7)
  build [scope]          Build dataset (default: m7)
  fast-build [scope]     Fast build with deepseek-r1:1.5b
  refresh [scope]        Alias for build

Build Management:
  create-build           Create timestamped build directory
  release-build          Promote latest build to release
  clean                  Clean local build artifacts
  build-status           Check build status

Data Management:
  etl-status             Check ETL status
  run-job                Run ETL job
  build-schema           Build database schema
  import-data            Import data
  check-coverage         Check data coverage

Workflow Management:
  create-pr "TITLE" ISSUE Create/update PR with mandatory testing
  commit-data-changes    Stage data directory changes
  cleanup-branches       Clean merged branches (--dry-run, --auto)
  shutdown-all           Stop all services

Analysis & Reporting:
  dcf-analysis           Run DCF analysis
  dcf-report             Generate DCF report
  generate-report        Generate analysis report
  validate-strategy      Validate analysis strategy

SEC Integration:
  test-sec-integration   Test SEC integration
  test-sec-recall        Test SEC recall functionality
  verify-sec-data        Verify SEC data availability
  test-sec-config        Test SEC orthogonal configuration system

Status & Validation:
  status                 Quick environment status
  cache-status           Check cache status
  verify-env             Verify environment dependencies
  check-integrity        Check data integrity

Git Hooks Management:
  install-hooks          Install pre-push hook to enforce create-pr workflow
  check-hooks            Check if git hooks are properly installed

Agent Execution Monitoring (Issue #180):
  monitoring-summary     Show 7-day agent execution monitoring summary
  monitoring-report      Export comprehensive monitoring report to JSON
  monitoring-stats       Show raw execution statistics (JSON format)

Scopes: f2 m7 n100 v3k (default: m7)
  f2     - Fast 2 companies (development testing)
  m7     - Magnificent 7 (standard/PR testing)
  n100   - NASDAQ 100 (validation testing)
  v3k    - VTI 3500+ (production testing)

Tips:
  - Add completion: source ./scripts/p3-completion.zsh
  - Add to PATH:    export PATH="$PROJECT_ROOT:$PATH"
  - All commands route through unified Python CLI system
"""
        print(help_text)

    def show_available_commands(self):
        """Show available commands when unknown command is used."""
        print("Available commands:")
        for cmd in sorted(self.commands.keys()):
            print(f"  {cmd}")
        print("\nUse 'p3 help' for detailed information.")

    def execute(self, args: List[str]):
        """Execute p3 command with arguments."""
        if not args or args[0] in ["help", "--help", "-h"]:
            self.show_help()
            return

        command = args[0]
        cmd_args = args[1:]

        if command not in self.commands:
            print(f"❌ Unknown command: {command}")
            self.show_available_commands()
            sys.exit(1)

        # Initialize execution monitoring
        monitor = None
        if MONITORING_ENABLED:
            monitor = get_monitor()
            task_description = f"{command} {' '.join(cmd_args)}"
            monitor.start_execution("p3-command", task_description, command)

        try:
            # Handle special commands
            special_cmd = self._handle_special_commands(command, cmd_args)
            if special_cmd is None and command == "activate":
                if monitor:
                    monitor.log_execution(ExecutionResult.SUCCESS)
                return  # activate command prints message and exits

            if special_cmd:
                cmd_string = special_cmd
            else:
                # Handle scope-based commands
                cmd_string = self._handle_scope_command(command, cmd_args)

                # Add remaining arguments
                if command not in [
                    "build",
                    "fast-build",
                    "refresh",
                    "e2e",
                    "create-pr",
                    "cleanup-branches",
                ]:
                    if cmd_args:
                        cmd_string += " " + " ".join(cmd_args)

            # CRITICAL FIX for Issue #153: Validate and sanitize command before execution
            validated_cmd = self._validate_command_syntax(cmd_string)

            print(f"🚀 Executing: {validated_cmd}")

            # Change to project directory
            # CRITICAL FIX: For worktrees, ensure we stay in the current git context
            original_cwd = os.getcwd()

            # Only change directory if we're not already in a proper git worktree
            if "worktree" in str(Path.cwd()) and Path.cwd() == self.project_root:
                # Already in correct worktree directory - don't change
                pass
            else:
                os.chdir(self.project_root)

            print(f"📍 Executing in directory: {os.getcwd()}")

            # Execute the command
            result = subprocess.run(validated_cmd, shell=True)

            # Log execution result
            if monitor:
                if result.returncode == 0:
                    monitor.log_execution(ExecutionResult.SUCCESS)
                else:
                    error_msg = f"Command failed with exit code {result.returncode}"
                    monitor.log_execution(ExecutionResult.FAILURE, error_message=error_msg)

            sys.exit(result.returncode)

        except Exception as e:
            # Log execution failure
            if monitor:
                import traceback

                stack_trace = traceback.format_exc()
                monitor.log_execution(
                    ExecutionResult.FAILURE, error_message=str(e), stack_trace=stack_trace
                )
            raise


def main():
    """Main entry point."""
    cli = P3CLI()
    cli.execute(sys.argv[1:])


if __name__ == "__main__":
    main()
