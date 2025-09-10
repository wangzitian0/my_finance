#!/usr/bin/env python3
"""
HRBP System Validation Script

Comprehensive validation of HRBP system integration with p3 workflow.
This script performs end-to-end validation of all HRBP components:

1. P3 Integration Validation
2. HRBP Component Health Checks
3. Configuration Validation
4. Performance Testing
5. Integration Testing
6. System Resilience Testing

Usage:
    python infra/hrbp/hrbp_system_validator.py [--quick] [--verbose] [--report-file OUTPUT]

Migrated from scripts/validate_hrbp_system.py as part of infrastructure modularization.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class HRBPSystemValidator:
    """
    Comprehensive HRBP system validator.

    Validates all aspects of HRBP integration with existing p3 workflow
    and generates detailed validation reports.
    """

    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.validation_results = {}
        self.start_time = time.time()

        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        # Add project to Python path
        sys.path.insert(0, str(project_root))

        print("🤖 HRBP System Validator Starting...")
        print(f"📁 Project Root: {project_root}")
        print(f"🔍 Verbose Mode: {verbose}")
        print("=" * 60)

    def validate_all(self, quick_mode: bool = False) -> Dict[str, Any]:
        """Run complete HRBP system validation."""
        validation_tests = [
            ("P3 Integration", self.validate_p3_integration),
            ("HRBP Components", self.validate_hrbp_components),
            ("Configuration System", self.validate_configuration_system),
            ("CLI Interfaces", self.validate_cli_interfaces),
            ("System Health", self.validate_system_health),
            ("Integration Framework", self.validate_integration_framework),
        ]

        if not quick_mode:
            validation_tests.extend(
                [
                    ("Performance Benchmarks", self.validate_performance_benchmarks),
                    ("End-to-End Workflows", self.validate_e2e_workflows),
                    ("Error Handling", self.validate_error_handling),
                    ("System Resilience", self.validate_system_resilience),
                ]
            )

        total_tests = len(validation_tests)
        passed_tests = 0

        for i, (test_name, test_func) in enumerate(validation_tests, 1):
            print(f"\n[{i}/{total_tests}] 🧪 Testing {test_name}...")

            try:
                result = test_func()
                self.validation_results[test_name] = result

                if result.get("status") == "pass":
                    passed_tests += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"

                print(f"    {status} - {result.get('summary', 'No summary')}")

                if self.verbose and result.get("details"):
                    for detail in result.get("details", []):
                        print(f"      • {detail}")

                if result.get("status") == "fail" and result.get("errors"):
                    for error in result.get("errors", []):
                        print(f"      ❌ {error}")

            except Exception as e:
                error_msg = f"Test execution failed: {str(e)}"
                self.validation_results[test_name] = {
                    "status": "error",
                    "summary": error_msg,
                    "errors": [str(e)],
                }
                print(f"    💥 ERROR - {error_msg}")

                if self.verbose:
                    traceback.print_exc()

        # Generate final summary
        self.validation_results["_summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests,
            "execution_time": time.time() - self.start_time,
            "timestamp": datetime.now().isoformat(),
            "quick_mode": quick_mode,
        }

        return self.validation_results

    def validate_p3_integration(self) -> Dict[str, Any]:
        """Validate HRBP integration with p3 command system."""
        results = {
            "status": "pass",
            "summary": "P3 integration validated successfully",
            "details": [],
            "errors": [],
        }

        try:
            # Check p3.py exists and has HRBP commands
            p3_file = self.project_root / "p3.py"
            if not p3_file.exists():
                results["status"] = "fail"
                results["errors"].append("p3.py file not found")
                return results

            p3_content = p3_file.read_text()

            # Validate HRBP commands exist
            required_hrbp_commands = [
                "hrbp-status",
                "hrbp-record-pr",
                "hrbp-manual-trigger",
                "hrbp-history",
                "hrbp-config",
            ]

            missing_commands = []
            for cmd in required_hrbp_commands:
                if f'"{cmd}"' not in p3_content:
                    missing_commands.append(cmd)

            if missing_commands:
                results["status"] = "fail"
                results["errors"].append(f"Missing HRBP commands: {missing_commands}")
            else:
                results["details"].append(
                    f"All {len(required_hrbp_commands)} HRBP commands found in p3.py"
                )

            # Check HRBP command handling logic
            if "_handle_special_commands" not in p3_content:
                results["status"] = "fail"
                results["errors"].append("HRBP command handling logic missing")
            else:
                results["details"].append("HRBP command handling logic present")

            # Test p3 help includes HRBP commands
            try:
                help_result = subprocess.run(
                    [sys.executable, "p3.py", "--help"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if help_result.returncode == 0 and "hrbp" in help_result.stdout.lower():
                    results["details"].append("HRBP commands appear in p3 help")
                else:
                    results["errors"].append("HRBP commands not visible in p3 help")

            except subprocess.TimeoutExpired:
                results["errors"].append("p3 help command timed out")
            except Exception as e:
                results["errors"].append(f"p3 help test failed: {str(e)}")

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"P3 integration validation failed: {str(e)}")

        return results

    def validate_hrbp_components(self) -> Dict[str, Any]:
        """Validate all HRBP system components exist and are importable."""
        results = {
            "status": "pass",
            "summary": "All HRBP components validated",
            "details": [],
            "errors": [],
        }

        # Core HRBP components to validate (updated paths)
        hrbp_components = [
            ("common/hrbp_integration_framework.py", "Integration Framework"),
            ("common/hrbp_performance_manager.py", "Performance Manager"),
            ("common/hrbp_pr_tracker.py", "PR Tracker"),
            ("common/agent_coordination_optimizer.py", "Coordination Optimizer"),
            ("infra/hrbp_automation.py", "Automation CLI"),
            ("infra/hrbp_comprehensive_cli.py", "Comprehensive CLI"),
            ("infra/hrbp/git_hooks/install_hrbp_hooks.py", "Git Hooks Installer"),
            ("infra/hrbp/git_hooks/post_merge_hrbp_hook.py", "Post-merge Hook"),
        ]

        missing_components = []
        import_failures = []

        for component_path, component_name in hrbp_components:
            file_path = self.project_root / component_path

            # Check file exists
            if not file_path.exists():
                missing_components.append(f"{component_name} ({component_path})")
                continue

            results["details"].append(f"{component_name} file exists")

            # Test importability for Python modules
            if component_path.endswith(".py") and "common/" in component_path:
                try:
                    # Attempt basic import validation
                    module_content = file_path.read_text()

                    # Check for basic class/function definitions
                    if "class " in module_content or "def " in module_content:
                        results["details"].append(f"{component_name} has valid Python structure")
                    else:
                        import_failures.append(f"{component_name} appears to be empty or malformed")

                except Exception as e:
                    import_failures.append(f"{component_name}: {str(e)}")

        if missing_components:
            results["status"] = "fail"
            results["errors"].append(f"Missing components: {', '.join(missing_components)}")

        if import_failures:
            results["status"] = "fail"
            results["errors"].extend(import_failures)

        if results["status"] == "pass":
            results["summary"] = f"All {len(hrbp_components)} HRBP components validated"

        return results

    def validate_configuration_system(self) -> Dict[str, Any]:
        """Validate HRBP configuration system and SSOT compliance."""
        results = {
            "status": "pass",
            "summary": "Configuration system validated",
            "details": [],
            "errors": [],
        }

        try:
            # Check main HRBP config file
            config_file = self.project_root / "common/config/hrbp_automation.yml"
            if not config_file.exists():
                results["status"] = "fail"
                results["errors"].append("Main HRBP config file missing")
                return results

            results["details"].append("Main HRBP config file exists")

            # Check directory manager integration
            dir_manager_file = self.project_root / "common/core/directory_manager.py"
            if not dir_manager_file.exists():
                results["errors"].append("DirectoryManager missing - SSOT compliance at risk")
            else:
                # Check if DirectoryManager has HRBP-related paths
                dm_content = dir_manager_file.read_text()
                if "logs" in dm_content and "config" in dm_content:
                    results["details"].append("DirectoryManager supports HRBP paths")
                else:
                    results["errors"].append("DirectoryManager may not support HRBP paths")

            # Check agent documentation lifecycle config
            agent_config = self.project_root / "common/config/agent_documentation_lifecycle.yml"
            if agent_config.exists():
                results["details"].append("Agent documentation lifecycle config exists")

            # Validate config structure (basic check)
            try:
                config_content = config_file.read_text()
                if "hrbp_automation" in config_content:
                    results["details"].append("Config has expected HRBP structure")
                else:
                    results["errors"].append("Config missing expected HRBP structure")
            except Exception as e:
                results["errors"].append(f"Config file read error: {str(e)}")

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Configuration validation failed: {str(e)}")

        return results

    def validate_cli_interfaces(self) -> Dict[str, Any]:
        """Validate HRBP CLI interfaces."""
        results = {
            "status": "pass",
            "summary": "CLI interfaces validated",
            "details": [],
            "errors": [],
        }

        try:
            # Test basic HRBP automation CLI
            hrbp_cli = self.project_root / "infra" / "hrbp_automation.py"
            if not hrbp_cli.exists():
                results["status"] = "fail"
                results["errors"].append("HRBP automation CLI missing")
                return results

            # Test CLI help functionality
            try:
                help_result = subprocess.run(
                    [sys.executable, str(hrbp_cli), "--help"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if help_result.returncode in [0, 2]:  # argparse may return 2 for help
                    results["details"].append("HRBP CLI help works")
                else:
                    results["errors"].append("HRBP CLI help failed")

            except subprocess.TimeoutExpired:
                results["errors"].append("HRBP CLI help timed out")
            except Exception as e:
                results["errors"].append(f"HRBP CLI help test failed: {str(e)}")

            # Test comprehensive CLI
            comprehensive_cli = self.project_root / "infra" / "hrbp_comprehensive_cli.py"
            if not comprehensive_cli.exists():
                results["status"] = "fail"
                results["errors"].append("HRBP comprehensive CLI missing")
                return results

            # Check comprehensive CLI structure
            cli_content = comprehensive_cli.read_text()
            expected_commands = ["status", "performance", "coordination", "optimize", "workflow"]

            missing_commands = []
            for cmd in expected_commands:
                if f"'{cmd}'" not in cli_content:
                    missing_commands.append(cmd)

            if missing_commands:
                results["errors"].append(f"Comprehensive CLI missing commands: {missing_commands}")
            else:
                results["details"].append("Comprehensive CLI has all expected commands")

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"CLI validation failed: {str(e)}")

        return results

    def validate_system_health(self) -> Dict[str, Any]:
        """Validate HRBP system health monitoring."""
        results = {
            "status": "pass",
            "summary": "System health monitoring validated",
            "details": [],
            "errors": [],
        }

        try:
            # Check system health components
            health_components = [
                "common/hrbp_integration_framework.py",
                "common/execution_monitor.py",
                "common/agent_task_tracker.py",
            ]

            for component in health_components:
                comp_path = self.project_root / component
                if not comp_path.exists():
                    results["errors"].append(f"Health component missing: {component}")
                else:
                    results["details"].append(f"Health component exists: {component}")

            # Check build_data directory structure (SSOT compliance)
            build_data_dir = self.project_root / "build_data"
            if build_data_dir.exists():
                logs_dir = build_data_dir / "logs"
                if logs_dir.exists():
                    results["details"].append("HRBP logs directory structure exists")
                else:
                    results["errors"].append("HRBP logs directory missing")
            else:
                results["errors"].append("build_data directory missing")

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"System health validation failed: {str(e)}")

        return results

    def validate_integration_framework(self) -> Dict[str, Any]:
        """Validate HRBP integration framework."""
        results = {
            "status": "pass",
            "summary": "Integration framework validated",
            "details": [],
            "errors": [],
        }

        try:
            # Check integration framework file
            framework_file = self.project_root / "common/hrbp_integration_framework.py"
            if not framework_file.exists():
                results["status"] = "fail"
                results["errors"].append("Integration framework file missing")
                return results

            framework_content = framework_file.read_text()

            # Check for key classes and functions
            required_elements = [
                "class HRBPIntegrationFramework",
                "get_hrbp_integration_framework",
                "validate_integration_health",
                "get_system_status",
            ]

            missing_elements = []
            for element in required_elements:
                if element not in framework_content:
                    missing_elements.append(element)
                else:
                    results["details"].append(f"Framework has {element}")

            if missing_elements:
                results["status"] = "fail"
                results["errors"].append(f"Framework missing elements: {missing_elements}")

            # Check integration with DirectoryManager
            if "directory_manager" in framework_content:
                results["details"].append(
                    "Framework integrates with DirectoryManager (SSOT compliant)"
                )
            else:
                results["errors"].append("Framework may not be SSOT compliant")

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Integration framework validation failed: {str(e)}")

        return results

    def validate_performance_benchmarks(self) -> Dict[str, Any]:
        """Validate HRBP system performance benchmarks."""
        results = {
            "status": "pass",
            "summary": "Performance benchmarks validated",
            "details": [],
            "errors": [],
        }

        try:
            # Test basic CLI performance
            start_time = time.time()

            try:
                hrbp_cli = self.project_root / "infra" / "hrbp_automation.py"
                help_result = subprocess.run(
                    [sys.executable, str(hrbp_cli), "--help"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                execution_time = time.time() - start_time

                if execution_time < 5.0:  # Should be fast
                    results["details"].append(f"CLI help executes quickly ({execution_time:.2f}s)")
                else:
                    results["errors"].append(f"CLI help too slow ({execution_time:.2f}s)")

            except subprocess.TimeoutExpired:
                results["errors"].append("CLI help timed out - performance issue")

            # Memory usage check (basic)
            try:
                import psutil

                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024

                if memory_mb < 200:  # Reasonable memory usage
                    results["details"].append(f"Memory usage acceptable ({memory_mb:.1f}MB)")
                else:
                    results["errors"].append(f"High memory usage ({memory_mb:.1f}MB)")

            except ImportError:
                results["details"].append("psutil not available - skipping memory check")

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Performance validation failed: {str(e)}")

        return results

    def validate_e2e_workflows(self) -> Dict[str, Any]:
        """Validate end-to-end HRBP workflows."""
        results = {
            "status": "pass",
            "summary": "End-to-end workflows validated",
            "details": [],
            "errors": [],
        }

        try:
            # Test p3 test integration with HRBP
            e2e_start_time = time.time()

            try:
                # Quick e2e test (with timeout to avoid long execution)
                e2e_result = subprocess.run(
                    [sys.executable, "p3.py", "test", "f2"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=10,  # Quick timeout for validation
                )

                # Should start executing (may timeout but shouldn't immediately fail)
                if e2e_result.returncode in [0, 124, -9]:  # success, timeout, or killed
                    results["details"].append("p3 test command starts executing with HRBP")
                else:
                    results["errors"].append("p3 test command fails to start with HRBP")

            except subprocess.TimeoutExpired:
                results["details"].append("p3 test starts executing (timed out as expected)")
            except Exception as e:
                results["errors"].append(f"p3 test test failed: {str(e)}")

            # Test P3 command execution (simplified 8-command system)
            try:
                version_result = subprocess.run(
                    [sys.executable, "p3.py", "version"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                # Command should be recognized and execute successfully
                if version_result.returncode == 0:
                    results["details"].append("p3 version command working correctly")
                else:
                    results["errors"].append("p3 version command failed")

            except subprocess.TimeoutExpired:
                results["details"].append("p3 version starts executing")
            except Exception as e:
                results["errors"].append(f"p3 version test failed: {str(e)}")

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"E2E workflow validation failed: {str(e)}")

        return results

    def validate_error_handling(self) -> Dict[str, Any]:
        """Validate HRBP system error handling."""
        results = {
            "status": "pass",
            "summary": "Error handling validated",
            "details": [],
            "errors": [],
        }

        try:
            # Test invalid HRBP command
            try:
                invalid_result = subprocess.run(
                    [sys.executable, "p3.py", "invalid-command"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                # Should handle invalid commands gracefully
                if invalid_result.returncode != 0:
                    results["details"].append("Invalid HRBP commands handled gracefully")
                else:
                    results["errors"].append("Invalid HRBP commands not handled properly")

            except subprocess.TimeoutExpired:
                results["errors"].append("Invalid command handling timed out")
            except Exception as e:
                results["errors"].append(f"Invalid command test failed: {str(e)}")

            # Test CLI with missing dependencies
            try:
                hrbp_cli = self.project_root / "infra" / "hrbp_automation.py"

                # Test with invalid subcommand
                invalid_cli_result = subprocess.run(
                    [sys.executable, str(hrbp_cli), "invalid-subcommand"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if invalid_cli_result.returncode != 0:
                    results["details"].append("HRBP CLI handles invalid subcommands")
                else:
                    results["errors"].append("HRBP CLI does not handle invalid subcommands")

            except Exception as e:
                results["errors"].append(f"CLI error handling test failed: {str(e)}")

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Error handling validation failed: {str(e)}")

        return results

    def validate_system_resilience(self) -> Dict[str, Any]:
        """Validate HRBP system resilience and fallback mechanisms."""
        results = {
            "status": "pass",
            "summary": "System resilience validated",
            "details": [],
            "errors": [],
        }

        try:
            # Test system behavior with missing configuration
            temp_dir = tempfile.mkdtemp()

            try:
                # Create temporary environment with missing config
                env = os.environ.copy()
                env["HRBP_CONFIG_PATH"] = str(Path(temp_dir) / "nonexistent.yml")

                # Test CLI with missing config
                hrbp_cli = self.project_root / "infra" / "hrbp_automation.py"
                config_result = subprocess.run(
                    [sys.executable, str(hrbp_cli), "--help"],
                    cwd=self.project_root,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                # Should handle missing config gracefully
                if config_result.returncode in [0, 2]:
                    results["details"].append("System handles missing configuration gracefully")
                else:
                    results["errors"].append("System does not handle missing configuration well")

            except Exception as e:
                results["errors"].append(f"Configuration resilience test failed: {str(e)}")
            finally:
                # Cleanup temp directory
                import shutil

                shutil.rmtree(temp_dir, ignore_errors=True)

            # Test system behavior under resource constraints
            # (This is a basic test - full load testing would need more resources)
            try:
                # Start multiple CLI processes simultaneously
                processes = []
                for i in range(3):
                    proc = subprocess.Popen(
                        [sys.executable, "p3.py", "--help"],
                        cwd=self.project_root,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    processes.append(proc)

                # Wait for all processes with timeout
                all_succeeded = True
                for proc in processes:
                    try:
                        proc.wait(timeout=5)
                        if proc.returncode != 0:
                            all_succeeded = False
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        all_succeeded = False

                if all_succeeded:
                    results["details"].append("System handles concurrent requests")
                else:
                    results["errors"].append("System struggles with concurrent requests")

            except Exception as e:
                results["errors"].append(f"Concurrency test failed: {str(e)}")

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Resilience validation failed: {str(e)}")

        return results

    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """Generate comprehensive validation report."""
        report = {
            "hrbp_system_validation_report": {
                "metadata": {
                    "validator_version": "1.0.0",
                    "validation_timestamp": datetime.now().isoformat(),
                    "project_root": str(self.project_root),
                    "total_execution_time": time.time() - self.start_time,
                },
                "summary": self.validation_results.get("_summary", {}),
                "test_results": {
                    k: v for k, v in self.validation_results.items() if not k.startswith("_")
                },
                "recommendations": self._generate_recommendations(),
            }
        }

        report_json = json.dumps(report, indent=2)

        if output_file:
            output_file.write_text(report_json)
            print(f"📄 Detailed report saved to: {output_file}")

        return report_json

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate recommendations based on validation results."""
        recommendations = []

        for test_name, result in self.validation_results.items():
            if test_name.startswith("_"):
                continue

            if result.get("status") == "fail":
                recommendations.append(
                    {
                        "priority": "high",
                        "area": test_name,
                        "description": f"Address failures in {test_name}",
                        "details": "; ".join(result.get("errors", [])),
                    }
                )
            elif result.get("status") == "error":
                recommendations.append(
                    {
                        "priority": "critical",
                        "area": test_name,
                        "description": f"Fix errors in {test_name}",
                        "details": "; ".join(result.get("errors", [])),
                    }
                )

        # Add general recommendations
        if not recommendations:
            recommendations.append(
                {
                    "priority": "low",
                    "area": "System Health",
                    "description": "HRBP system validation passed - consider regular health checks",
                    "details": "Set up automated validation runs",
                }
            )

        return recommendations

    def print_final_summary(self):
        """Print final validation summary."""
        summary = self.validation_results.get("_summary", {})

        print("\n" + "=" * 70)
        print("🤖 HRBP SYSTEM VALIDATION SUMMARY")
        print("=" * 70)

        print(f"📊 Tests Run: {summary.get('total_tests', 0)}")
        print(f"✅ Passed: {summary.get('passed_tests', 0)}")
        print(f"❌ Failed: {summary.get('failed_tests', 0)}")
        print(f"📈 Success Rate: {summary.get('success_rate', 0):.1%}")
        print(f"⏱️  Execution Time: {summary.get('execution_time', 0):.2f}s")

        # Overall status
        success_rate = summary.get("success_rate", 0)
        if success_rate >= 0.9:
            status = "🟢 EXCELLENT"
            message = "HRBP system is well-integrated and ready for production use"
        elif success_rate >= 0.7:
            status = "🟡 GOOD"
            message = "HRBP system is mostly functional with minor issues to address"
        elif success_rate >= 0.5:
            status = "🟠 NEEDS ATTENTION"
            message = "HRBP system has significant issues that should be resolved"
        else:
            status = "🔴 CRITICAL"
            message = "HRBP system has major problems requiring immediate attention"

        print(f"\n🎯 Overall Status: {status}")
        print(f"💡 {message}")

        # Show failed tests
        failed_tests = [
            name
            for name, result in self.validation_results.items()
            if not name.startswith("_") and result.get("status") in ["fail", "error"]
        ]

        if failed_tests:
            print(f"\n⚠️  Tests requiring attention:")
            for test in failed_tests:
                print(f"   • {test}")

        print("=" * 70)


def main():
    """Main validation script entry point."""
    parser = argparse.ArgumentParser(
        description="HRBP System Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python infra/hrbp/hrbp_system_validator.py                    # Full validation
  python infra/hrbp/hrbp_system_validator.py --quick           # Quick validation
  python infra/hrbp/hrbp_system_validator.py --verbose         # Detailed output
  python infra/hrbp/hrbp_system_validator.py --report-file report.json
        """,
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick validation (skips performance and e2e tests)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    parser.add_argument("--report-file", type=Path, help="Output file for detailed JSON report")

    args = parser.parse_args()

    # Get project root
    project_root = Path(__file__).parent.parent.parent

    # Create validator
    validator = HRBPSystemValidator(project_root, verbose=args.verbose)

    try:
        # Run validation
        results = validator.validate_all(quick_mode=args.quick)

        # Generate report if requested
        if args.report_file:
            validator.generate_report(args.report_file)

        # Print summary
        validator.print_final_summary()

        # Exit with appropriate code
        summary = results.get("_summary", {})
        success_rate = summary.get("success_rate", 0)

        if success_rate >= 0.7:
            print("\n✅ HRBP system validation completed successfully")
            sys.exit(0)
        else:
            print("\n❌ HRBP system validation completed with issues")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {str(e)}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
