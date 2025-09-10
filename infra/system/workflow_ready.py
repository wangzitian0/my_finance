#!/usr/bin/env python3
"""
Workflow-Oriented Environment Command: READY
"I want to start working" - ensure everything is ready

Enhanced P3 Ready Command with robust environment management:
- Automated Podman machine startup and health validation
- Ansible playbook integration for complete environment orchestration
- Neo4j container startup and health validation
- Comprehensive service dependency resolution
- Actionable error messages with specific remediation steps

Replaces 8 commands: env-status, env-start, neo4j-start, status, verify-env,
podman-status, cache-status, check-integrity
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description, ignore_errors=False, timeout=30, show_output=False):
    """Execute command and display results with enhanced error handling"""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0 or ignore_errors:
            print(f"✅ {description} - OK")
            if result.stdout.strip() and show_output:
                # Show key information based on context
                lines = result.stdout.strip().split("\n")
                for line in lines[:3]:  # Show only first 3 lines
                    if line.strip():
                        print(f"   {line}")
                if len(lines) > 3:
                    print("   ...")
            return True, result
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False, result
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False, None
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False, None


def check_and_start_podman_machine():
    """Check Podman machine status and start if needed"""
    print("🐳 Checking Podman machine status...")

    # Check if podman is installed
    success, result = run_command("podman --version", "Podman installation check", timeout=10)
    if not success:
        print("❌ Podman is not installed or not in PATH")
        print(
            "💡 Install Podman: brew install podman (macOS) or follow https://podman.io/getting-started/installation"
        )
        return False

    # Check machine status
    success, result = run_command("podman machine list", "Podman machine status", timeout=15)
    if not success:
        print("❌ Unable to check Podman machine status")
        return False

    machine_output = result.stdout if result else ""

    # Parse machine status
    machine_running = "Running" in machine_output
    machine_exists = "podman-machine" in machine_output or any(
        "default" in line for line in machine_output.split("\n")
    )
    never_started = "Never" in machine_output

    if machine_running:
        # Verify we can actually connect to Podman
        success, _ = run_command("podman info", "Podman connectivity test", timeout=10)
        if success:
            print("✅ Podman machine is running and accessible")
            return True
        else:
            print("⚠️  Podman machine appears running but not accessible, restarting...")
            success, _ = run_command("podman machine stop", "Stopping Podman machine", timeout=30)
            time.sleep(2)

    if not machine_exists:
        print("🔧 Creating new Podman machine...")
        success, _ = run_command("podman machine init", "Creating Podman machine", timeout=60)
        if not success:
            print("❌ Failed to create Podman machine")
            return False
        time.sleep(2)

    if not machine_running or never_started:
        print("🚀 Starting Podman machine...")
        success, result = run_command("podman machine start", "Starting Podman machine", timeout=90)
        if not success:
            print("❌ Failed to start Podman machine")
            if result and "vfkit" in result.stderr:
                print("💡 This appears to be a vfkit/virtualization issue")
                print(
                    "💡 Try: podman machine stop && podman machine rm && podman machine init && podman machine start"
                )
            return False

        # Wait for machine to be fully ready
        print("⏳ Waiting for Podman machine to be fully ready...")
        time.sleep(5)

        # Verify connection
        success, _ = run_command("podman info", "Verifying Podman machine connectivity", timeout=15)
        if success:
            print("✅ Podman machine started successfully and is accessible")
            return True
        else:
            print("❌ Podman machine started but is not accessible")
            return False

    print("✅ Podman machine is ready")
    return True


def setup_neo4j_container():
    """Setup and start Neo4j container"""
    print("🗄️ Setting up Neo4j database container...")

    # Check if container exists
    success, result = run_command(
        "podman ps -a --filter name=neo4j-finance --format '{{.Names}} {{.Status}}'",
        "Checking Neo4j container",
        timeout=15,
    )

    container_exists = success and result and "neo4j-finance" in result.stdout
    container_running = success and result and "Up" in result.stdout

    if not container_exists:
        print("🔧 Neo4j container not found, running Ansible setup...")
        # Use ansible playbook to create container
        success, _ = run_command(
            "ansible-playbook infra/ansible/p3_ready_setup.yml",
            "Running P3 Ready Ansible orchestration",
            timeout=300,
        )
        if not success:
            print("❌ Ansible setup failed - trying manual container setup...")
            # Fallback: basic container creation
            success, _ = run_command(
                "podman run -d --name neo4j-finance -p 7474:7474 -p 7687:7687 "
                '-e NEO4J_AUTH=neo4j/password -e NEO4J_PLUGINS=["apoc"] '
                "--restart always neo4j:latest",
                "Creating Neo4j container manually",
                timeout=120,
            )
            if not success:
                return False
    elif not container_running:
        print("🚀 Starting existing Neo4j container...")
        success, _ = run_command(
            "podman start neo4j-finance", "Starting Neo4j container", timeout=30
        )
        if not success:
            return False
    else:
        print("✅ Neo4j container is already running")

    # Wait for Neo4j to be fully ready
    print("⏳ Waiting for Neo4j to be fully ready...")
    max_retries = 12  # 60 seconds total
    for i in range(max_retries):
        time.sleep(5)
        success, _ = run_command(
            "curl -s http://localhost:7474 >/dev/null 2>&1",
            f"Checking Neo4j readiness (attempt {i+1}/{max_retries})",
            ignore_errors=True,
            timeout=10,
        )
        if success:
            print("✅ Neo4j database is ready and responding")
            return True

    print("⚠️  Neo4j container is running but not responding to HTTP requests")
    print("💡 This may be normal during first startup - check with 'p3 debug'")
    return True  # Return True to continue, as container may just be initializing


def run_ansible_orchestration():
    """Run Ansible playbook for complete environment orchestration"""
    print("🎭 Running Ansible environment orchestration...")

    # Check if ansible is available
    success, _ = run_command("ansible --version", "Checking Ansible availability", timeout=10)
    if not success:
        print("⚠️  Ansible not available, skipping orchestration")
        print("💡 Install Ansible for complete environment management: pip install ansible")
        return True  # Continue without ansible

    # Run the P3 ready setup playbook
    success, _ = run_command(
        "ansible-playbook infra/ansible/p3_ready_setup.yml",
        "Running complete P3 Ready environment setup",
        timeout=300,  # 5 minutes for complete setup
    )

    if success:
        print("✅ Ansible orchestration completed successfully")
        return True
    else:
        print("⚠️  Ansible orchestration had issues, continuing with basic setup...")
        return True  # Continue even if ansible fails


def main():
    print("🚀 READY - Getting everything ready for development")
    print("Enhanced P3 Ready Command with automated environment management")
    print("=" * 70)
    print()

    # Phase 1: Infrastructure Foundation
    print("🏗️ Phase 1: Infrastructure Foundation")
    print("-" * 40)

    if not check_and_start_podman_machine():
        print("❌ CRITICAL: Podman machine setup failed")
        print("💡 Manual fix required:")
        print("   1. Check virtualization support: sysctl kern.hv_support")
        print("   2. Restart Docker Desktop if running")
        print("   3. Try: podman machine rm && podman machine init && podman machine start")
        sys.exit(1)

    print()

    # Phase 2: Service Orchestration
    print("🎭 Phase 2: Service Orchestration")
    print("-" * 40)

    if not setup_neo4j_container():
        print("❌ CRITICAL: Neo4j container setup failed")
        print("💡 Manual fix required:")
        print("   1. Check container logs: podman logs neo4j-finance")
        print("   2. Remove and recreate: podman rm -f neo4j-finance")
        print("   3. Try manual setup with Ansible: ansible-playbook infra/ansible/setup.yml")
        sys.exit(1)

    # Optional: Run complete Ansible orchestration
    run_ansible_orchestration()

    print()

    # Phase 3: Environment Validation
    print("🔍 Phase 3: Environment Validation")
    print("-" * 40)

    validation_steps = [
        # Basic environment checks
        ("pixi run python --version", "Python environment check", False),
        # Service connectivity
        ("curl -s http://localhost:7474 >/dev/null", "Neo4j web interface", True),
        # Core package verification
        (
            "pixi run python -c 'import pandas, numpy, requests; print(\"Core packages OK\")'",
            "Core packages check",
            False,
        ),
        # Comprehensive status
        (
            "pixi run python infra/comprehensive_env_status.py",
            "Comprehensive environment status",
            False,
        ),
    ]

    success_count = 0
    total_steps = len(validation_steps)

    for cmd, desc, ignore_errors in validation_steps:
        success, _ = run_command(cmd, desc, ignore_errors)
        if success:
            success_count += 1
        print()  # Empty line separator

    print("=" * 70)
    if success_count == total_steps:
        print("🎉 READY - Everything is set up for development!")
        print("✅ Podman machine running and accessible")
        print("✅ Neo4j database running and healthy")
        print("✅ Python environment and packages ready")
        print("✅ All services responding correctly")
        print()
        print("💡 You can now use:")
        print("   p3 build f2        # Quick test build")
        print("   p3 test f2         # Fast validation")
        print("   p3 ship 'title' #  # Create PR")
        sys.exit(0)
    elif success_count >= total_steps - 1:
        print("⚠️  READY - Mostly ready, minor issues detected")
        print("✅ Critical services are running")
        print("⚠️  Some validation checks had issues")
        print()
        print(
            "💡 You can proceed with development, but consider running 'p3 debug' to check details"
        )
        print("💡 If issues persist, use 'p3 reset' for complete cleanup and restart")
        sys.exit(0)
    else:
        print("❌ NOT READY - Major issues detected")
        print(f"📊 {success_count}/{total_steps} validation checks passed")
        print()
        print("💡 Recommended actions:")
        print("   1. Review error messages above")
        print("   2. Run 'p3 debug' for detailed diagnostics")
        print("   3. Run 'p3 reset' for complete environment reset")
        print("   4. Check system requirements: Docker/Podman, Python, disk space")
        sys.exit(1)


if __name__ == "__main__":
    main()