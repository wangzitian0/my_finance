#!/usr/bin/env python3
"""
Workflow-Oriented Command: DEBUG
"Diagnose issues" - enhanced unified status check with actionable recommendations

Enhanced Debug Command Features:
- Comprehensive infrastructure status checks
- Detailed Podman machine diagnostics
- Neo4j container health validation
- Environment connectivity testing
- Actionable remediation recommendations
- Performance and resource monitoring
"""

import subprocess
import sys
import time
from pathlib import Path


def run_check(cmd, description, timeout=10, show_all_output=False):
    """Run diagnostic check with enhanced error reporting."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            if result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                max_lines = len(lines) if show_all_output else min(5, len(lines))
                for line in lines[:max_lines]:
                    if line.strip():
                        print(f"   {line}")
                if len(lines) > max_lines:
                    print("   ...")
        else:
            print(f"❌ {description} - ISSUE DETECTED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout.strip():
                print(
                    f"   Output: {result.stdout.strip()[:200]}{'...' if len(result.stdout.strip()) > 200 else ''}"
                )
        return result.returncode == 0, result
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT ({timeout}s)")
        return False, None
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False, None


def diagnose_podman_issues():
    """Detailed Podman machine diagnostics"""
    print("\n🐳 PODMAN MACHINE DIAGNOSTICS")
    print("-" * 30)

    # Check installation
    success, result = run_check("podman --version", "Podman installation")
    if not success:
        print("💡 RECOMMENDATION: Install Podman with 'brew install podman' (macOS)")
        return

    # Check machine status
    success, result = run_check("podman machine list", "Machine status", show_all_output=True)
    if success and result:
        machine_output = result.stdout
        if "Running" in machine_output:
            print("✅ Podman machine appears to be running")
            # Test connectivity
            conn_success, _ = run_check("podman info", "Machine connectivity test")
            if not conn_success:
                print("💡 ISSUE: Machine running but not accessible")
                print("💡 RECOMMENDATION: Run 'p3 ready' to restart machine")
        elif "Never" in machine_output:
            print("⚠️  Machine exists but never started (likely vfkit issue)")
            print("💡 RECOMMENDATION: Run 'p3 ready' to start machine")
        else:
            print("⚠️  Machine is not running")
            print("💡 RECOMMENDATION: Run 'p3 ready' to start machine")

    # Check system resources
    success, _ = run_check("vm_stat | head -5", "System memory status")


def diagnose_neo4j_issues():
    """Detailed Neo4j container and connectivity diagnostics"""
    print("\n🗄️ NEO4J DIAGNOSTICS")
    print("-" * 20)

    # Check container existence and status
    success, result = run_check(
        "podman ps -a --filter name=neo4j-finance --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'",
        "Neo4j container status",
    )

    if not success or not result or "neo4j-finance" not in result.stdout:
        print("❌ Neo4j container not found")
        print("💡 RECOMMENDATION: Run 'p3 ready' to create and start container")
        return

    if "Up" in result.stdout:
        print("✅ Neo4j container is running")

        # Test web interface
        web_success, _ = run_check(
            "curl -s --max-time 5 http://localhost:7474/browser/ >/dev/null 2>&1",
            "Web interface connectivity",
        )
        if web_success:
            print("✅ Neo4j web interface is accessible")
        else:
            print("⚠️  Web interface not responding")
            print("💡 Container may still be starting up")

        # Test database port
        db_success, _ = run_check("nc -z localhost 7687", "Database port connectivity")
        if db_success:
            print("✅ Neo4j database port is accessible")
        else:
            print("⚠️  Database port not accessible")

        # Show recent logs
        print("\n📋 Recent Neo4j container logs:")
        run_check("podman logs neo4j-finance --tail 10", "Container logs", show_all_output=True)
    else:
        print("❌ Neo4j container is not running")
        print("💡 RECOMMENDATION: Run 'p3 ready' to start container")

        # Show why container stopped
        run_check("podman logs neo4j-finance --tail 5", "Container stop logs")


def diagnose_python_environment():
    """Python environment and package diagnostics"""
    print("\n🐍 PYTHON ENVIRONMENT DIAGNOSTICS")
    print("-" * 35)

    # Check pixi environment
    success, _ = run_check("pixi --version", "Pixi installation")
    if not success:
        print("💡 RECOMMENDATION: Install Pixi from https://pixi.sh/")
        return

    # Check Python version
    success, _ = run_check("pixi run python --version", "Python version")
    if not success:
        print("💡 RECOMMENDATION: Run 'pixi install' to setup environment")
        return

    # Check critical packages
    critical_packages = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("requests", "requests"),
        ("neo4j", "neo4j"),
        ("yaml", "yaml"),
    ]

    print("\n📦 Critical package checks:")
    missing_packages = []
    for package, import_name in critical_packages:
        success, _ = run_check(
            f"pixi run python -c 'import {import_name}; print(f\"{import_name} OK\")'",
            f"Package {package}",
        )
        if not success:
            missing_packages.append(package)

    if missing_packages:
        print(f"💡 RECOMMENDATION: Missing packages: {', '.join(missing_packages)}")
        print("💡 Run 'pixi install' to install missing packages")


def diagnose_data_architecture():
    """Data directory and build architecture diagnostics"""
    print("\n📁 DATA ARCHITECTURE DIAGNOSTICS")
    print("-" * 32)

    # Check main data directory
    success, _ = run_check("ls -la build_data/", "Data directory structure")
    if not success:
        print("❌ build_data/ directory missing")
        print("💡 RECOMMENDATION: Run 'p3 ready' to initialize data structure")
        return

    # Check stage directories
    stage_dirs = [
        "build_data/stage_00_raw",
        "build_data/stage_01_daily_delta",
        "build_data/stage_04_query_results",
        "build_data/logs",
    ]

    print("\n📊 Stage directory status:")
    for stage_dir in stage_dirs:
        success, result = run_check(
            f"ls -la {stage_dir}/ 2>/dev/null | wc -l", f"Stage {stage_dir.split('_')[-1]}"
        )
        if success and result:
            file_count = int(result.stdout.strip()) - 1  # Subtract 1 for total line
            print(f"   Files: {file_count}")


def provide_comprehensive_recommendations():
    """Provide comprehensive troubleshooting recommendations"""
    print("\n🛠️ COMPREHENSIVE TROUBLESHOOTING GUIDE")
    print("=" * 45)

    print("\n🚀 QUICK FIXES (try first):")
    print("   1. p3 ready    - Complete environment setup")
    print("   2. p3 reset    - Nuclear reset (if ready fails)")

    print("\n🔧 MANUAL DIAGNOSTICS:")
    print("   1. Check system resources: Activity Monitor")
    print("   2. Check Docker Desktop conflicts")
    print("   3. Check port availability: lsof -i :7474")
    print("   4. Check disk space: df -h")

    print("\n⚙️ ADVANCED FIXES:")
    print("   1. Podman machine reset: podman machine rm && podman machine init")
    print("   2. Container reset: podman rm -f neo4j-finance")
    print("   3. Pixi environment reset: pixi clean && pixi install")
    print("   4. Port conflict resolution: sudo lsof -ti:7474 | xargs kill")


def main():
    print("🔍 DEBUG - Enhanced Environment Diagnostics")
    print("P3 Debug Command with comprehensive infrastructure analysis")
    print("=" * 65)

    # Phase 1: Basic Environment Checks
    print("\n🏗️ PHASE 1: BASIC ENVIRONMENT")
    print("-" * 30)

    basic_checks = [
        ("pwd", "Current directory"),
        ("whoami", "Current user"),
        ("git branch --show-current", "Current branch"),
        ("git status --short", "Git status"),
    ]

    for cmd, desc in basic_checks:
        run_check(cmd, desc)

    # Phase 2: Infrastructure Diagnostics
    print("\n🏭 PHASE 2: INFRASTRUCTURE DIAGNOSTICS")
    print("-" * 35)

    diagnose_podman_issues()
    diagnose_neo4j_issues()

    # Phase 3: Application Environment
    print("\n🎯 PHASE 3: APPLICATION ENVIRONMENT")
    print("-" * 32)

    diagnose_python_environment()
    diagnose_data_architecture()

    # Phase 4: Performance and Resource Checks
    print("\n📊 PHASE 4: PERFORMANCE & RESOURCES")
    print("-" * 32)

    performance_checks = [
        ("df -h | head -5", "Disk space"),
        ("ps aux | grep -E '(podman|neo4j)' | head -5", "Process status"),
        ("lsof -i :7474,7687 2>/dev/null", "Port usage"),
    ]

    for cmd, desc in performance_checks:
        run_check(cmd, desc)

    # Phase 5: Recommendations
    provide_comprehensive_recommendations()

    print("\n" + "=" * 65)
    print("🎯 DEBUG COMPLETE - Review diagnostics above")
    print("💡 Start with 'p3 ready' for automated fixes")
    print("💡 Use 'p3 reset' if ready command fails")


if __name__ == "__main__":
    main()
