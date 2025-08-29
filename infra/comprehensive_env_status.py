#!/usr/bin/env python3
"""
Comprehensive Environment Status Checker
Checks all environment dependencies and provides actionable feedback
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from common.core.directory_manager import directory_manager

    DIRECTORY_MANAGER_AVAILABLE = True
except ImportError:
    DIRECTORY_MANAGER_AVAILABLE = False


def run_command(cmd: str) -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timeout"
    except Exception as e:
        return False, str(e)


def check_pixi() -> Dict:
    """Check Pixi environment"""
    success, output = run_command("pixi --version")
    status = {
        "name": "Pixi Package Manager",
        "status": "✅ Ready" if success else "❌ Not Available",
        "details": output if success else "Install: https://pixi.sh/",
        "commands": ["pixi shell", "p3 env setup"] if not success else [],
    }
    return status


def check_podman() -> Dict:
    """Check Podman installation and machine status"""
    # Check installation
    installed, version = run_command("podman --version")
    if not installed:
        return {
            "name": "Podman Container Engine",
            "status": "❌ Not Installed",
            "details": "Install with: brew install podman",
            "commands": ["brew install podman", "p3 env setup"],
        }

    # Check machine status
    machine_running, machine_info = run_command("podman machine list")
    machine_status = "Running" in machine_info if machine_running else False
    never_started = "Never" in machine_info if machine_running else False

    # Check if we can connect to Podman
    can_connect, _ = run_command("podman info")

    if can_connect:
        status_text = "✅ Ready"
        details = f"Version: {version}, Machine: Running"
        commands = []
    elif machine_status:
        status_text = "⚠️ Machine Running but Not Connected"
        details = "Machine is running but podman commands fail"
        commands = ["podman machine stop", "podman machine start"]
    elif never_started:
        status_text = "❌ Machine Never Started (vfkit issue)"
        details = f"Version: {version}, Machine exists but failed to start"
        commands = ["p3 env start"]
    else:
        status_text = "❌ Machine Not Running"
        details = f"Version: {version}, Machine: Stopped"
        commands = ["p3 env start"]

    return {
        "name": "Podman Container Engine",
        "status": status_text,
        "details": details,
        "commands": commands,
    }


def check_neo4j() -> Dict:
    """Check Neo4j container status"""
    # Check if container exists and is running
    exists, container_info = run_command(
        "podman ps -a --filter name=neo4j-finance --format '{{.Status}}'"
    )

    if not exists or not container_info:
        return {
            "name": "Neo4j Database",
            "status": "❌ Container Not Found",
            "details": "Neo4j container not deployed",
            "commands": ["p3 env start"],
        }

    is_running = "Up" in container_info

    if is_running:
        # Check if Neo4j is actually responding
        responding, _ = run_command("curl -s http://localhost:7474 >/dev/null")
        if responding:
            status_text = "✅ Ready"
            details = f"Status: {container_info}, Web: http://localhost:7474"
            commands = []
        else:
            status_text = "⚠️ Starting Up"
            details = f"Container running but not yet responding"
            commands = ["p3 neo4j logs"]
    else:
        status_text = "❌ Container Stopped"
        details = f"Status: {container_info}"
        commands = ["p3 neo4j start"]

    return {
        "name": "Neo4j Database",
        "status": status_text,
        "details": details,
        "commands": commands,
    }


def check_data_directory() -> Dict:
    """Check build_data directory (current data architecture)"""
    if DIRECTORY_MANAGER_AVAILABLE:
        # Use directory manager to get the proper data path
        data_root = directory_manager.get_data_root()

        if not data_root.exists():
            return {
                "name": "Data Directory",
                "status": "❌ Missing",
                "details": f"Data directory not found at {data_root}",
                "commands": ["p3 env setup"],
            }

        # Check if legacy data symlink exists (should not)
        legacy_data_path = Path("data")
        if legacy_data_path.exists():
            return {
                "name": "Data Directory",
                "status": "⚠️ Legacy Data Symlink Found",
                "details": f"Legacy data/ symlink found. Current architecture uses {data_root}",
                "commands": ["rm -rf data", "# Data now at build_data/"],
            }
    else:
        # Fallback: check for build_data directory directly
        data_root = Path("build_data")

        if not data_root.exists():
            return {
                "name": "Data Directory",
                "status": "❌ Missing",
                "details": "build_data/ directory not found",
                "commands": ["p3 env setup"],
            }

    return {
        "name": "Data Directory",
        "status": "✅ Ready",
        "details": f"Data architecture ready at {data_root}",
        "commands": [],
    }


def check_python_deps() -> Dict:
    """Check key Python dependencies"""
    # Map package names to their import names
    deps_to_check = {
        "pandas": "pandas",
        "numpy": "numpy",
        "neo4j": "neo4j",
        "requests": "requests",
        "pyyaml": "yaml",  # Package name vs import name
    }
    missing = []

    for package_name, import_name in deps_to_check.items():
        # Use pixi environment to ensure consistency with other p3 commands
        success, _ = run_command(f"pixi run python -c 'import {import_name}'")
        if not success:
            missing.append(package_name)

    if not missing:
        return {
            "name": "Python Dependencies",
            "status": "✅ Ready",
            "details": f"All key packages available: {', '.join(deps_to_check.keys())}",
            "commands": [],
        }
    else:
        return {
            "name": "Python Dependencies",
            "status": "⚠️ Missing Packages",
            "details": f"Missing: {', '.join(missing)}",
            "commands": ["pixi install"],
        }


def main():
    """Main status check function"""
    print("🩺 Comprehensive Environment Status Check")
    print("=" * 60)

    checks = [
        check_pixi(),
        check_podman(),
        check_neo4j(),
        check_data_directory(),
        check_python_deps(),
    ]

    all_ready = True
    fix_commands = []

    for check in checks:
        print(f"\n🔍 {check['name']}")
        print(f"   {check['status']}")
        print(f"   {check['details']}")

        if "❌" in check["status"] or "⚠️" in check["status"]:
            all_ready = False
            if check["commands"]:
                fix_commands.extend(check["commands"])

    print("\n" + "=" * 60)

    if all_ready:
        print("✅ All systems ready! You can start development.")
        print("\n🚀 Quick start commands:")
        print("   p3 build run f2        # Quick test build")
        print("   p3 e2e                 # Full test")
        print("   p3 neo4j connect       # Connect to database")
    else:
        print("❌ Some components need attention.")
        print("\n🔧 Recommended fix sequence:")
        for i, cmd in enumerate(set(fix_commands), 1):
            print(f"   {i}. {cmd}")

        print("\n💡 Or run the complete setup:")
        print("   p3 env setup")

    return 0 if all_ready else 1


if __name__ == "__main__":
    sys.exit(main())
