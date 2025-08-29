#!/usr/bin/env python3
"""
HRBP System Initialization Script

Initializes the complete HRBP (Human Resources Business Partner) automation
system for agent performance management and coordination optimization.

This script:
1. Validates system dependencies and configuration
2. Initializes all HRBP components
3. Performs integration health checks
4. Sets up monitoring and logging
5. Validates system readiness

Usage:
    python infra/init_hrbp_system.py [--validate-only] [--reset]
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple


def main():
    """Main initialization routine."""
    parser = argparse.ArgumentParser(
        description="Initialize HRBP System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python infra/init_hrbp_system.py                    # Full initialization
  python infra/init_hrbp_system.py --validate-only    # Validation checks only
  python infra/init_hrbp_system.py --reset            # Reset and reinitialize
        """,
    )

    parser.add_argument(
        "--validate-only", action="store_true", help="Only run validation checks, do not initialize"
    )

    parser.add_argument(
        "--reset", action="store_true", help="Reset existing HRBP data before initialization"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    print("🚀 HRBP System Initialization")
    print("=" * 50)

    try:
        # Add project root to Python path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        # Run initialization sequence
        success = run_initialization_sequence(args)

        if success:
            print("\n✅ HRBP System initialization completed successfully!")
            if not args.validate_only:
                print("\n🎯 Next steps:")
                print("   1. Test the system: python infra/hrbp_comprehensive_cli.py status")
                print(
                    "   2. Run performance analysis: python infra/hrbp_comprehensive_cli.py performance"
                )
                print(
                    "   3. Check integration health: python infra/hrbp_comprehensive_cli.py integration-health"
                )
            sys.exit(0)
        else:
            print("\n❌ HRBP System initialization failed!")
            print("   Review the error messages above and fix any issues.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Initialization cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Initialization error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def run_initialization_sequence(args) -> bool:
    """
    Run the complete HRBP initialization sequence.

    Args:
        args: Command line arguments

    Returns:
        True if initialization successful, False otherwise
    """
    print("🔍 Phase 1: System Validation")
    print("-" * 30)

    # Phase 1: Validate system dependencies
    validation_results = validate_system_dependencies(args.verbose)

    if not validation_results["success"]:
        print(f"❌ System validation failed: {validation_results['error']}")
        return False

    print("✅ System validation passed")

    if args.validate_only:
        print("\n🔍 Validation-only mode: skipping initialization")
        return True

    # Phase 2: Directory and file setup
    print("\n📁 Phase 2: Directory Structure Setup")
    print("-" * 40)

    setup_results = setup_directory_structure(args.reset, args.verbose)
    if not setup_results["success"]:
        print(f"❌ Directory setup failed: {setup_results['error']}")
        return False

    print("✅ Directory structure setup complete")

    # Phase 3: Component initialization
    print("\n⚙️  Phase 3: Component Initialization")
    print("-" * 35)

    component_results = initialize_hrbp_components(args.verbose)
    if not component_results["success"]:
        print(f"❌ Component initialization failed: {component_results['error']}")
        return False

    print("✅ HRBP components initialized")

    # Phase 4: Integration setup
    print("\n🔗 Phase 4: Integration Setup")
    print("-" * 28)

    integration_results = setup_integrations(args.verbose)
    if not integration_results["success"]:
        print(f"⚠️  Integration setup completed with warnings: {integration_results['warning']}")
        # Continue - integrations can have warnings but still work
    else:
        print("✅ Integration setup complete")

    # Phase 5: Final validation
    print("\n🏥 Phase 5: System Health Check")
    print("-" * 30)

    health_results = validate_system_health(args.verbose)
    if not health_results["success"]:
        print(f"❌ System health check failed: {health_results['error']}")
        return False

    print("✅ System health check passed")

    return True


def validate_system_dependencies(verbose: bool = False) -> Dict:
    """Validate system dependencies and requirements."""
    try:
        # Check Python version
        if verbose:
            print(f"   🐍 Python version: {sys.version}")

        # Check required Python modules
        required_modules = ["json", "pathlib", "logging", "datetime", "dataclasses"]
        optional_modules = ["yaml"]

        for module in required_modules:
            try:
                __import__(module)
                if verbose:
                    print(f"   ✅ Required module: {module}")
            except ImportError:
                return {"success": False, "error": f"Required module {module} not available"}

        for module in optional_modules:
            try:
                __import__(module)
                if verbose:
                    print(f"   ✅ Optional module: {module}")
            except ImportError:
                if verbose:
                    print(f"   ⚠️  Optional module: {module} not available (will use fallbacks)")

        # Check file system permissions
        current_dir = Path.cwd()
        test_file = current_dir / "test_write_permission.tmp"

        try:
            test_file.write_text("test")
            test_file.unlink()
            if verbose:
                print(f"   ✅ Write permissions: {current_dir}")
        except PermissionError:
            return {"success": False, "error": f"No write permissions in {current_dir}"}

        # Check if we're in the right directory
        expected_files = ["p3", "pixi.toml", "common/config"]
        missing_files = []

        for expected in expected_files:
            if not (current_dir / expected).exists():
                missing_files.append(expected)

        if missing_files:
            return {
                "success": False,
                "error": f'Missing expected files/dirs: {", ".join(missing_files)}. Run from project root.',
            }

        if verbose:
            print(f"   ✅ Project structure: valid")

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}


def setup_directory_structure(reset: bool = False, verbose: bool = False) -> Dict:
    """Setup HRBP directory structure and configuration files."""
    try:
        from common.directory_manager import directory_manager

        # Get paths
        logs_dir = directory_manager.get_logs_path()
        config_dir = directory_manager.get_config_path()

        # Create directories if they don't exist
        directories_created = []

        if not logs_dir.exists():
            logs_dir.mkdir(parents=True, exist_ok=True)
            directories_created.append(str(logs_dir))

        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
            directories_created.append(str(config_dir))

        # Create agent local directories (if they don't exist)
        agents_local_dir = Path("agents/local")
        if not agents_local_dir.exists():
            agents_local_dir.mkdir(parents=True, exist_ok=True)
            directories_created.append(str(agents_local_dir))

        if verbose and directories_created:
            for dir_path in directories_created:
                print(f"   📁 Created directory: {dir_path}")

        # Reset data if requested
        if reset:
            reset_files = [
                logs_dir / "hrbp_pr_counter.json",
                logs_dir / "hrbp_trigger_history.json",
                logs_dir / "agent_performance_data.json",
                logs_dir / "coordination_metrics.json",
            ]

            for file_path in reset_files:
                if file_path.exists():
                    file_path.unlink()
                    if verbose:
                        print(f"   🗑️  Reset file: {file_path}")

        # Validate configuration file exists
        hrbp_config_file = config_dir / "hrbp_automation.yml"
        if not hrbp_config_file.exists():
            if verbose:
                print(f"   ⚠️  HRBP config file not found: {hrbp_config_file}")
                print(f"   📝 System will use default configuration")
        else:
            if verbose:
                print(f"   ✅ HRBP config file: {hrbp_config_file}")

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}


def initialize_hrbp_components(verbose: bool = False) -> Dict:
    """Initialize HRBP system components."""
    try:
        components_initialized = []

        # Initialize performance manager
        try:
            from common.hrbp_performance_manager import get_hrbp_performance_manager

            performance_manager = get_hrbp_performance_manager()
            components_initialized.append("performance_manager")
            if verbose:
                print(f"   ⚙️  Performance Manager: initialized")
        except Exception as e:
            if verbose:
                print(f"   ❌ Performance Manager: {e}")
            raise

        # Initialize coordination optimizer
        try:
            from common.agent_coordination_optimizer import get_coordination_optimizer

            optimizer = get_coordination_optimizer()
            components_initialized.append("coordination_optimizer")
            if verbose:
                print(f"   ⚙️  Coordination Optimizer: initialized")
        except Exception as e:
            if verbose:
                print(f"   ❌ Coordination Optimizer: {e}")
            raise

        # Initialize PR tracker
        try:
            from common.hrbp_pr_tracker import get_hrbp_tracker

            pr_tracker = get_hrbp_tracker()
            components_initialized.append("pr_tracker")
            if verbose:
                print(f"   ⚙️  PR Tracker: initialized")
        except Exception as e:
            if verbose:
                print(f"   ❌ PR Tracker: {e}")
            raise

        # Initialize integration framework
        try:
            from common.hrbp_integration_framework import get_hrbp_integration_framework

            framework = get_hrbp_integration_framework()
            components_initialized.append("integration_framework")
            if verbose:
                print(f"   ⚙️  Integration Framework: initialized")
        except Exception as e:
            if verbose:
                print(f"   ❌ Integration Framework: {e}")
            raise

        # Test component interactions
        try:
            status = framework.get_system_status()
            if verbose:
                print(f"   🔗 Component interaction test: passed")
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Component interaction test: {e}")
            # Don't fail initialization for interaction issues

        return {"success": True, "components_initialized": components_initialized}

    except Exception as e:
        return {"success": False, "error": str(e)}


def setup_integrations(verbose: bool = False) -> Dict:
    """Setup HRBP system integrations."""
    try:
        from common.hrbp_integration_framework import get_hrbp_integration_framework

        framework = get_hrbp_integration_framework()

        # Test P3 integration
        p3_success = framework.integrate_with_p3_system()
        if verbose:
            status_icon = "✅" if p3_success else "❌"
            print(
                f"   {status_icon} P3 system integration: {'successful' if p3_success else 'failed'}"
            )

        # Test Git-ops integration
        git_success = framework.integrate_with_git_ops()
        if verbose:
            status_icon = "✅" if git_success else "❌"
            print(
                f"   {status_icon} Git-ops integration: {'successful' if git_success else 'failed'}"
            )

        # Overall integration status
        if p3_success and git_success:
            return {"success": True}
        elif p3_success or git_success:
            warning = "Some integrations failed but core functionality available"
            return {"success": True, "warning": warning}
        else:
            return {"success": False, "error": "All integrations failed"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def validate_system_health(verbose: bool = False) -> Dict:
    """Validate overall HRBP system health."""
    try:
        from common.hrbp_integration_framework import get_hrbp_integration_framework

        framework = get_hrbp_integration_framework()

        # Run comprehensive health check
        health_report = framework.validate_integration_health()

        overall_status = health_report.get("overall_status", "unknown")
        issues = health_report.get("issues_detected", [])

        if verbose:
            print(f"   🏥 Overall health: {overall_status}")
            if issues:
                print(f"   ⚠️  Issues detected: {len(issues)}")
                for issue in issues[:3]:  # Show first 3 issues
                    print(f"      - {issue}")
                if len(issues) > 3:
                    print(f"      ... and {len(issues) - 3} more")
            else:
                print(f"   ✅ No issues detected")

        # Determine success based on health status
        if overall_status in ["healthy", "degraded"]:
            return {"success": True, "health_status": overall_status}
        else:
            return {"success": False, "error": f"System health: {overall_status}", "issues": issues}

    except Exception as e:
        return {"success": False, "error": str(e)}


def show_system_info():
    """Display comprehensive system information after successful initialization."""
    try:
        from common.hrbp_integration_framework import get_hrbp_integration_framework

        framework = get_hrbp_integration_framework()
        system_status = framework.get_system_status()

        print("\n📊 System Information:")
        print(f"   Version: {system_status.get('system_version', 'unknown')}")
        print(
            f"   Framework Status: {system_status.get('integration_framework_status', 'unknown')}"
        )

        # Health status
        health = system_status.get("integration_health", {})
        health_status = health.get("overall_status", "unknown")
        print(f"   Health Status: {health_status}")

        # Integration status
        integration_status = health.get("integration_status", {})
        print(f"   P3 Integration: {'✅' if integration_status.get('p3_integration') else '❌'}")
        print(
            f"   Git-ops Integration: {'✅' if integration_status.get('git_ops_integration') else '❌'}"
        )

    except Exception as e:
        print(f"   ⚠️  Could not retrieve system info: {e}")


if __name__ == "__main__":
    main()
