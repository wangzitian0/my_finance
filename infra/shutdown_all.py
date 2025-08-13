#!/usr/bin/env python3
"""
Shutdown All Services Script
This script safely shuts down all running services for the finance project.
Supports both Minikube and local Neo4j setups.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description, ignore_errors=False):
    """Run a command and handle errors gracefully."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0 or ignore_errors:
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"⚠️  {description} failed: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ {description} error: {e}")


def shutdown_minikube():
    """Shutdown Minikube cluster if running."""
    # Check if Minikube is running first
    result = subprocess.run("minikube status", shell=True, capture_output=True, text=True)
    if result.returncode == 0 and "running" in result.stdout.lower():
        run_command("minikube stop", "Stopping Minikube cluster")
    else:
        print("ℹ️  Minikube is not running")


def shutdown_neo4j():
    """Shutdown local Neo4j database if running."""
    # Check if Neo4j is running first
    result = subprocess.run("neo4j status", shell=True, capture_output=True, text=True)
    if result.returncode == 0 and "running" in result.stdout.lower():
        run_command("neo4j stop", "Stopping Neo4j database")
    else:
        print("ℹ️  Neo4j is not running")


def cleanup_processes():
    """Clean up any remaining background processes."""
    processes_to_check = ["java.*neo4j", "python.*spider", "python.*etl", "minikube"]

    for process_pattern in processes_to_check:
        cmd = f"pkill -f '{process_pattern}'"
        run_command(
            cmd,
            f"Cleaning up processes matching: {process_pattern}",
            ignore_errors=True,
        )


def main():
    """Main shutdown sequence."""
    print("🛑 Shutting down all finance project services...")
    print("=" * 50)

    # 1. Stop Minikube cluster
    shutdown_minikube()

    # 2. Stop local Neo4j database
    shutdown_neo4j()

    # 3. Give services time to shut down gracefully
    print("⏳ Waiting for services to shut down gracefully...")
    time.sleep(3)

    # 4. Clean up any remaining processes
    cleanup_processes()

    # 5. Final status check
    print("\n" + "=" * 50)
    print("🔍 Final status check:")

    # Check Minikube status
    minikube_result = subprocess.run("minikube status", shell=True, capture_output=True, text=True)
    if minikube_result.returncode == 0 and "running" in minikube_result.stdout.lower():
        print("⚠️  Minikube: Still running")
    else:
        print("✅ Minikube: Stopped")

    # Check Neo4j status
    neo4j_result = subprocess.run("neo4j status", shell=True, capture_output=True, text=True)
    if neo4j_result.returncode == 0 and "running" in neo4j_result.stdout.lower():
        print("⚠️  Neo4j: Still running")
    else:
        print("✅ Neo4j: Stopped")

    print("\n🎉 Shutdown sequence completed!")
    print("\n💡 To restart services:")
    print("   • Full setup: p3 env setup")
    print("   • Start services: p3 env start")


if __name__ == "__main__":
    main()
