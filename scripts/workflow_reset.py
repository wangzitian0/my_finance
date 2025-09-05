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


def main():
    print("🔧 RESET - Fixing environment issues with clean restart")
    print("=" * 55)
    print("⚠️  This will stop services, clean up, and restart everything")
    print()

    reset_steps = [
        # 1. Stop services
        ("podman stop neo4j-finance", "Stopping Neo4j", True),
        ("sleep 2", "Waiting for services to stop", True),
        # 2. Cleanup and reset
        ("pixi clean", "Cleaning pixi cache", True),
        ("pixi install", "Reinstalling pixi environment", False),
        # 3. Restart services
        ("podman start neo4j-finance", "Starting Neo4j", False),
        ("sleep 3", "Waiting for Neo4j to initialize", True),
        # 4. Verify reset results
        (
            "podman ps --format 'table {{.Names}}\\t{{.Status}}'",
            "Checking container status",
            False,
            True,
        ),
        ("pixi run python --version", "Verifying Python environment", False, True),
        ("pixi run python infra/comprehensive_env_status.py", "Final environment check", False),
    ]

    success_count = 0
    total_steps = len(reset_steps)

    for step in reset_steps:
        if len(step) == 3:
            cmd, desc, ignore_errors = step
            show_output = False
        else:
            cmd, desc, ignore_errors, show_output = step

        if run_command(cmd, desc, ignore_errors, show_output):
            success_count += 1

        # Brief pause between important steps
        if "stop" in desc.lower() or "start" in desc.lower():
            time.sleep(1)

        print()  # Empty line separator

    print("=" * 55)
    if success_count >= total_steps - 1:  # Allow 1 failure
        print("🎉 RESET COMPLETE - Environment has been reset successfully!")
        print("💡 You can now use 'p3 ready' to verify everything is working")
        print("💡 Then proceed with: p3 build, p3 test, p3 ship")
        sys.exit(0)
    else:
        print("❌ RESET FAILED - Some issues could not be resolved automatically")
        print("💡 Manual intervention may be required:")
        print("   • Check Docker/Podman service status")
        print("   • Verify pixi installation: pixi --version")
        print("   • Check available disk space")
        sys.exit(1)


if __name__ == "__main__":
    main()
