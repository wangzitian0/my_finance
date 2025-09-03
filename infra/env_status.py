#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
env_status.py

Unified environment status checker that provides all necessary information
about the development environment in a simple format.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, capture_output=True, text=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=text)
        return result.returncode == 0, result.stdout.strip() if capture_output else ""
    except Exception:
        return False, ""


def check_minikube():
    """Check Minikube status."""
    print("🔍 Checking Minikube...")

    # Check if minikube is installed
    success, _ = run_command("which minikube")
    if not success:
        print("  ❌ Minikube not installed")
        return False

    # Check if minikube is running
    success, output = run_command("minikube status")
    if success and "Running" in output:
        print("  ✅ Minikube is running")

        # Get IP
        success, ip = run_command("minikube ip")
        if success:
            print(f"  📍 Minikube IP: {ip}")
            return ip
    else:
        print("  ❌ Minikube is not running")
        print("  💡 Start with: p3 ready")

    return False


def check_neo4j(minikube_ip):
    """Check Neo4j status."""
    print("\n🔍 Checking Neo4j...")

    # Check if kubectl is available
    kubectl_cmd = "kubectl"
    success, _ = run_command("which kubectl")
    if not success:
        kubectl_cmd = "minikube kubectl --"

    # Check deployment
    success, output = run_command(f"{kubectl_cmd} get deployment neo4j")
    if not success:
        print("  ❌ Neo4j deployment not found")
        print("  💡 Deploy with: p3 ready")
        return

    # Check pod status
    success, output = run_command(
        f"{kubectl_cmd} get pods -l app=neo4j -o jsonpath='{{.items[*].status.phase}}'"
    )
    if success and "Running" in output:
        print("  ✅ Neo4j is running")

        if minikube_ip:
            print(f"  🌐 Web Interface: http://{minikube_ip}:30474")
            print(f"  🔌 Bolt Connection: bolt://{minikube_ip}:30687")
            print("  🔑 Credentials: neo4j / finance123")
    else:
        print("  ❌ Neo4j pod is not running")
        print("  💡 Check logs with: kubectl logs -l app=neo4j")


def check_pixi():
    """Check Pixi environment."""
    print("\n🔍 Checking Pixi...")

    success, _ = run_command("which pixi")
    if not success:
        print("  ❌ Pixi not installed")
        return False

    # Check if in pixi environment
    import os

    if "PIXI_ENV_DIR" in os.environ:
        print("  ✅ Pixi environment is active")

        # Check if pixi.toml exists
        if Path("pixi.toml").exists():
            print("  ✅ Project configuration found")
            return True
        else:
            print("  ❌ pixi.toml not found in current directory")
    else:
        print("  ❌ Not in Pixi shell")
        print("  💡 Run: pixi shell")

    return False


def show_quick_commands():
    """Show commonly used commands."""
    print("\n🚀 Quick Commands:")
    print("  Environment:")
    print("    p3 ready    - Start all services")
    print("    p3 reset     - Stop all services")
    print("    p3 reset    - Reset everything")
    print("    p3 debug   - This status check")
    print("\n  Development:")
    print("    p3 status       - Check data status")
    print("    p3 build run m7     - Build test dataset")
    print("    pixi run run-job      - Run data collection")
    print("\n  Code Quality:")
    print("    p3 check        - Validate code (format + lint + test)")
    print("    p3 test         - Comprehensive testing")
    print("    p3 test         - Run tests")


def main():
    """Main status check."""
    print("🩺 Development Environment Status")
    print("=" * 50)

    # Check all components
    minikube_ip = check_minikube()
    check_neo4j(minikube_ip)
    pixi_ok = check_pixi()

    print("\n" + "=" * 50)

    if minikube_ip and pixi_ok:
        print("✅ Environment is ready for development!")
        show_quick_commands()
    else:
        print("❌ Environment needs attention.")
        print("\n🔧 Setup steps:")
        if not pixi_ok:
            print("  1. Install Pixi: https://pixi.sh/")
            print("  2. Run: pixi shell")
        if not minikube_ip:
            print("  3. Run: p3 ready")
            print("  4. Run: p3 ready")


if __name__ == "__main__":
    main()
