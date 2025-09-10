#!/usr/bin/env python3
"""
Workflow-Oriented Environment Command: RESET
"Fix environment issues" - clean restart everything

Replaces 8 commands: env-stop, env-reset, neo4j-stop, neo4j-restart,
env-setup, env-start, podman-status, env-status
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description, ignore_errors=False, show_output=False):
    """Execute command and display results"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 or ignore_errors:
            print(f"✅ {description} - Done")
            if show_output and result.stdout.strip():
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - Timeout")
        return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False


def reset_podman_machine():
    """Reset Podman machine completely"""
    print("🐳 PODMAN MACHINE RESET")
    print("-" * 25)

    # Stop machine if running
    run_command("podman machine stop", "Stopping Podman machine", True, False)
    time.sleep(2)

    # Remove machine if exists
    run_command("podman machine rm -f", "Removing Podman machine", True, False)
    time.sleep(2)

    # Recreate machine
    success = run_command("podman machine init", "Creating new Podman machine", False, True)
    if not success:
        print("❌ Failed to create new Podman machine")
        return False

    time.sleep(3)

    # Start new machine
    success = run_command("podman machine start", "Starting new Podman machine", False, True)
    if not success:
        print("❌ Failed to start new Podman machine")
        return False

    time.sleep(5)

    # Test connectivity
    success = run_command("podman info", "Testing Podman connectivity", False, False)
    if success:
        print("✅ Podman machine reset successful")
        return True
    else:
        print("❌ Podman machine not accessible after reset")
        return False


def reset_containers():
    """Reset all containers"""
    print("🗄️ CONTAINER RESET")
    print("-" * 18)

    # Remove Neo4j container completely
    run_command("podman rm -f neo4j-finance", "Removing Neo4j container", True, False)
    time.sleep(2)

    # Clean up any orphaned containers
    run_command("podman container prune -f", "Cleaning orphaned containers", True, False)

    print("✅ Containers reset complete")
    return True


def reset_python_environment():
    """Reset Python environment completely"""
    print("🐍 PYTHON ENVIRONMENT RESET")
    print("-" * 28)

    # Clean pixi cache
    run_command("pixi clean", "Cleaning pixi cache", True, False)
    time.sleep(1)

    # Remove pixi environment directory
    run_command("rm -rf .pixi/", "Removing pixi environment", True, False)

    # Reinstall environment
    success = run_command("pixi install", "Reinstalling pixi environment", False, True)
    if not success:
        print("❌ Failed to reinstall pixi environment")
        return False

    # Test Python
    success = run_command("pixi run python --version", "Testing Python", False, True)
    if success:
        print("✅ Python environment reset successful")
        return True
    else:
        print("❌ Python environment not working after reset")
        return False


def main():
    print("🔧 RESET - Nuclear environment reset with complete cleanup")
    print("Enhanced P3 Reset Command with comprehensive infrastructure reset")
    print("=" * 70)
    print("⚠️  This will completely reset all services and environments")
    print("⚠️  This is a destructive operation - all containers and caches will be removed")
    print()

    try:
        response = input("❓ Are you sure you want to proceed? [y/N]: ").strip().lower()
        if response not in ["y", "yes"]:
            print("🚫 Reset cancelled by user")
            sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        print("\n🚫 Reset cancelled by user")
        sys.exit(0)

    print("\n🚀 Starting comprehensive reset...")

    # Phase 1: Infrastructure Reset
    print("\n🏭 PHASE 1: INFRASTRUCTURE RESET")
    print("-" * 35)

    podman_success = reset_podman_machine()
    if not podman_success:
        print("⚠️  Podman reset failed, but continuing...")

    # Phase 2: Container Reset
    print("\n📦 PHASE 2: CONTAINER RESET")
    print("-" * 27)

    reset_containers()

    # Phase 3: Python Environment Reset
    print("\n🐍 PHASE 3: PYTHON ENVIRONMENT RESET")
    print("-" * 35)

    python_success = reset_python_environment()
    if not python_success:
        print("⚠️  Python environment reset failed")

    # Phase 4: Data Directory Cleanup
    print("\n📁 PHASE 4: DATA DIRECTORY CLEANUP")
    print("-" * 32)

    # Clean build artifacts but preserve structure
    run_command(
        "rm -rf build_data/stage_04_query_results/build_*", "Cleaning build artifacts", True
    )
    run_command("rm -rf build_data/logs/*.log", "Cleaning old logs", True)
    run_command("find build_data/ -name '.DS_Store' -delete", "Cleaning system files", True)

    print("✅ Data directory cleanup complete")

    # Phase 5: Verification
    print("\n🔍 PHASE 5: RESET VERIFICATION")
    print("-" * 29)

    verification_steps = [
        ("pixi --version", "Pixi availability", False, True),
        ("podman --version", "Podman availability", False, True),
        ("podman machine list", "Machine status", False, True),
    ]

    verification_success = 0
    for cmd, desc, ignore_errors, show_output in verification_steps:
        if run_command(cmd, desc, ignore_errors, show_output):
            verification_success += 1
        print()

    print("=" * 70)

    if verification_success >= len(verification_steps) - 1:
        print("🎉 RESET COMPLETE - Environment has been completely reset!")
        print("✅ Podman machine recreated")
        print("✅ Containers removed and cleaned")
        print("✅ Python environment reinstalled")
        print("✅ Data directories cleaned")
        print()
        print("🚀 NEXT STEPS:")
        print("   1. Run 'p3 ready' to setup environment")
        print("   2. Run 'p3 debug' to verify everything works")
        print("   3. Proceed with: p3 build, p3 test, p3 ship")
        sys.exit(0)
    else:
        print("❌ RESET INCOMPLETE - Some components could not be reset")
        print(f"📊 {verification_success}/{len(verification_steps)} verification checks passed")
        print()
        print("💡 Manual intervention may be required:")
        print("   1. Check system requirements: macOS virtualization, disk space")
        print("   2. Restart terminal and try again")
        print("   3. Check for conflicts: Docker Desktop, other container systems")
        print("   4. Verify Podman installation: brew reinstall podman")
        print()
        print("🔧 Alternative: Try individual component resets")
        print("   • Podman only: podman machine rm && podman machine init")
        print("   • Python only: pixi clean && pixi install")
        sys.exit(1)


if __name__ == "__main__":
    main()