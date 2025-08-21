#!/usr/bin/env python3
"""
Unified p3 CLI for my_finance project
Centralizes all development commands under one consistent interface

This replaces the shell-based p3 script with a proper Python CLI system
as specified in Issue #111.
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


class P3CLI:
    """Unified p3 CLI system for my_finance project."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.commands = self._load_command_mapping()

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
            "clean": 'pixi run python -c \'import shutil; from pathlib import Path; build_dir = Path("data/stage_99_build"); [shutil.rmtree(d) for d in build_dir.glob("build_*") if d.is_dir()]; print("🧹 Cleaned")\'',
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
            "check-integrity": 'pixi run python -c \'from pathlib import Path; dirs = ["data/stage_00_original", "data/stage_01_extract", "data/stage_99_build"]; [print(f"📁 {d}: {"✅ exists" if Path(d).exists() else "❌ missing"}") for d in dirs]\'',
            "shutdown-all": "pixi run python infra/shutdown_all.py",
            # SEC Integration Commands (p3 calls pixi for Python execution)
            "test-sec-integration": "pixi run python dcf_engine/sec_integration_template.py",
            "test-sec-recall": "pixi run python dcf_engine/sec_recall_usage_example.py",
            "verify-sec-data": 'pixi run python -c \'from pathlib import Path; from collections import Counter; sec_files = list(Path("data/stage_01_extract/sec_edgar").rglob("*.txt")); print(f"📄 Found {len(sec_files)} total SEC documents"); ticker_counts = Counter(f.name.split("_")[0] for f in sec_files); print("📊 By ticker:"); [print(f"  - {ticker}: {count} files") for ticker, count in sorted(ticker_counts.items())]\'',
            # ETL and Data Commands (p3 calls pixi for Python execution)
            "etl-status": "pixi run python ETL/manage.py status",
            "run-job": "pixi run python ETL/run_job.py",
            "build-schema": "pixi run python ETL/build_schema.py",
            "import-data": "pixi run python ETL/import_data.py",
            "check-coverage": "pixi run python ETL/check_coverage.py",
            "migrate-data": "pixi run python ETL/migrate_data_structure.py",
            # Additional Build Commands (p3 calls pixi for Python execution)
            "build-size": 'pixi run python -c \'from pathlib import Path; import subprocess; result = subprocess.run(["du", "-sh", "data/stage_99_build"], capture_output=True, text=True); print(f"📦 Build directory size: {result.stdout.strip()}")\'',
            # Ollama and LLM Commands
            "build-sec-library": "pixi run python dcf_engine/sec_document_manager.py",
            "llm-dcf-report": "pixi run python dcf_engine/llm_dcf_generator.py --ticker AAPL",
            "hybrid-dcf-report": "pixi run python dcf_engine/legacy_testing/hybrid_dcf_analyzer.py",
            # Additional Analysis Commands
            "generate-report-legacy": "pixi run python dcf_engine/legacy_testing/generate_dcf_report.py",
            "backtest": "echo 'Backtest simulation completed (placeholder)' && pixi run python dcf_engine/legacy_testing/simple_m7_dcf.py",
            "test-semantic-retrieval": "pixi run python test_semantic_retrieval.py",
            # Legacy DCF Commands
            "dcf-analysis-legacy": "pixi run python dcf_engine/legacy_testing/m7_dcf_analysis.py",
            "dcf-report-legacy": "pixi run python dcf_engine/legacy_testing/generate_dcf_report.py",
            "simple-dcf-legacy": "pixi run python dcf_engine/legacy_testing/simple_m7_dcf.py",
            "hybrid-dcf-legacy": "pixi run python dcf_engine/legacy_testing/hybrid_dcf_analyzer.py",
            # Testing Commands
            "test-yfinance": "pixi run python ETL/tests/integration/test_yfinance.py",
            "test-config": "pixi run python -m pytest ETL/tests/test_config.py -v",
            "test-dcf-report": "pixi run python -m pytest dcf_engine/test_dcf_report.py -v",
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
                # E2E command maps to different behavior based on scope
                if resolved_scope == "f2":
                    return "pixi run python infra/create_pr_with_test.py --skip-pr-creation --fast-mode"
                else:
                    return (
                        "pixi run python infra/create_pr_with_test.py --skip-pr-creation"
                    )
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
            cmd = "pixi run python infra/cleanup_merged_branches.py"
            if "--dry-run" in args:
                cmd += " --dry-run"
            elif "--auto" in args:
                cmd += " --auto"
            return cmd

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

Status & Validation:
  status                 Quick environment status
  cache-status           Check cache status
  verify-env             Verify environment dependencies
  check-integrity        Check data integrity

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

        # Handle special commands
        special_cmd = self._handle_special_commands(command, cmd_args)
        if special_cmd is None and command == "activate":
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

        print(f"🚀 Executing: {cmd_string}")

        # Change to project directory
        os.chdir(self.project_root)

        # Execute the command
        result = subprocess.run(cmd_string, shell=True)
        sys.exit(result.returncode)


def main():
    """Main entry point."""
    cli = P3CLI()
    cli.execute(sys.argv[1:])


if __name__ == "__main__":
    main()
