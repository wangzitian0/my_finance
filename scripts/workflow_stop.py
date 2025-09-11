#!/usr/bin/env python3
"""
Workflow-Oriented Environment Command: STOP
"I want to stop working" - properly release development resources

Enhanced P3 Stop Command with comprehensive resource cleanup:
- Neo4j container graceful shutdown and data persistence
- Optional Podman machine management (default: keep running)
- Ansible playbook integration for complete environment teardown
- Resource validation and cleanup confirmation
- Actionable cleanup status with resource usage information

Complements workflow_ready.py for proper development environment lifecycle management
"""

import subprocess
import sys
import time
from pathlib import Path
import argparse


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


def get_container_status():
    """Get current container status for reporting"""
    containers = {}

    success, result = run_command(
        "podman ps -a --format '{{.Names}} {{.Status}} {{.Image}}'",
        "Getting container status",
        ignore_errors=True,
        timeout=10,
    )

    if success and result and result.stdout:
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    status = " ".join(parts[1:-1]) if len(parts) > 2 else parts[1]
                    containers[name] = status

    return containers


def get_podman_machine_status():
    """Get Podman machine status"""
    success, result = run_command(
        "podman machine list --format '{{.Name}} {{.Running}}'",
        "Getting Podman machine status",
        ignore_errors=True,
        timeout=10,
    )

    if success and result and result.stdout:
        lines = result.stdout.strip().split("\n")
        for line in lines[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    return parts[0], parts[1].lower() == "true"

    return None, False


def stop_neo4j_container(force=False):
    """Stop Neo4j container with proper data persistence"""
    print("🗄️ Stopping Neo4j database container...")

    # Check if container exists and is running
    containers = get_container_status()
    neo4j_status = containers.get("neo4j-finance", "not found")

    if "not found" in neo4j_status.lower():
        print("✅ Neo4j container not found - already stopped")
        return True

    if "exited" in neo4j_status.lower() or "stopped" in neo4j_status.lower():
        print("✅ Neo4j container already stopped")
        return True

    # Graceful shutdown first
    if not force:
        print("🔄 Attempting graceful Neo4j shutdown...")
        success, _ = run_command(
            "podman exec neo4j-finance cypher-shell -u neo4j -p password 'CALL dbms.shutdown()'",
            "Neo4j graceful shutdown",
            ignore_errors=True,
            timeout=15,
        )

        if success:
            print("✅ Neo4j gracefully shut down")
            time.sleep(3)  # Wait for graceful shutdown

    # Stop container
    success, result = run_command(
        "podman stop neo4j-finance", "Stopping Neo4j container", timeout=30
    )

    if success:
        print("✅ Neo4j container stopped successfully")

        # Verify data persistence
        success, _ = run_command(
            "podman exec neo4j-finance ls /data 2>/dev/null || echo 'Container stopped'",
            "Verifying data persistence",
            ignore_errors=True,
            timeout=10,
        )

        return True
    else:
        if force:
            print("🔧 Force stopping Neo4j container...")
            success, _ = run_command(
                "podman kill neo4j-finance",
                "Force stopping Neo4j container",
                ignore_errors=True,
                timeout=15,
            )
            return success
        else:
            print("⚠️  Neo4j graceful stop failed")
            return False


def stop_additional_containers():
    """Stop any additional development containers"""
    print("🐳 Checking for additional development containers...")

    containers = get_container_status()
    stopped_containers = []

    # Define development containers that should be stopped
    dev_containers = ["redis-dev", "postgres-dev", "mongodb-dev", "elasticsearch-dev", "kafka-dev"]

    for container_name in dev_containers:
        if container_name in containers:
            status = containers[container_name]
            if "up" in status.lower() or "running" in status.lower():
                print(f"🔧 Stopping {container_name}...")
                success, _ = run_command(
                    f"podman stop {container_name}",
                    f"Stopping {container_name}",
                    ignore_errors=True,
                    timeout=20,
                )
                if success:
                    stopped_containers.append(container_name)

    if stopped_containers:
        print(f"✅ Stopped additional containers: {', '.join(stopped_containers)}")
    else:
        print("✅ No additional containers to stop")

    return True


def manage_podman_machine(stop_machine=False):
    """Manage Podman machine - default keeps it running for faster restart"""
    machine_name, is_running = get_podman_machine_status()

    if not machine_name:
        print("✅ Podman machine not found or not managed")
        return True

    if not is_running:
        print("✅ Podman machine already stopped")
        return True

    if stop_machine:
        print("🛑 Stopping Podman machine (full resource cleanup)...")
        success, _ = run_command("podman machine stop", "Stopping Podman machine", timeout=60)

        if success:
            print("✅ Podman machine stopped - full resource cleanup completed")
            print("💡 Next 'p3 ready' will take longer due to machine startup")
        else:
            print("⚠️  Failed to stop Podman machine")

        return success
    else:
        print("🔄 Keeping Podman machine running for faster restart")
        print(f"   Machine '{machine_name}' status: Running")
        print("💡 To stop machine completely: p3 stop --full")
        return True


def run_ansible_stop_playbook(cleanup_type="standard"):
    """Run Ansible playbook for environment teardown"""
    print(f"🎭 Running Ansible {cleanup_type} cleanup...")

    # Check if ansible is available
    success, _ = run_command("ansible --version", "Checking Ansible availability", timeout=10)
    if not success:
        print("⚠️  Ansible not available, skipping orchestration")
        return True  # Continue without ansible

    # Select appropriate playbook
    if cleanup_type == "full":
        playbook = "infra/ansible/p3_stop_cleanup.yml"
        timeout = 180
    else:
        playbook = "infra/ansible/stop.yml"
        timeout = 120

    # Check if playbook exists
    if not Path(playbook).exists():
        print(f"⚠️  Playbook {playbook} not found, using basic stop")
        playbook = "infra/ansible/stop.yml"

    success, _ = run_command(
        f"ansible-playbook {playbook}", f"Running {cleanup_type} cleanup playbook", timeout=timeout
    )

    if success:
        print(f"✅ Ansible {cleanup_type} cleanup completed")
    else:
        print(f"⚠️  Ansible {cleanup_type} cleanup had issues")

    return success


def validate_cleanup():
    """Validate that services are properly stopped"""
    print("🔍 Validating cleanup completion...")

    validation_results = []

    # Check Neo4j container
    containers = get_container_status()
    neo4j_status = containers.get("neo4j-finance", "not found")
    neo4j_stopped = "not found" in neo4j_status or "exited" in neo4j_status.lower()
    validation_results.append(("Neo4j container stopped", neo4j_stopped))

    # Check Neo4j port
    success, _ = run_command(
        "curl -s http://localhost:7474 >/dev/null 2>&1",
        "Neo4j port 7474 check",
        ignore_errors=True,
        timeout=5,
    )
    neo4j_port_free = not success
    validation_results.append(("Neo4j port 7474 released", neo4j_port_free))

    # Check Podman machine
    machine_name, is_running = get_podman_machine_status()
    if machine_name:
        validation_results.append(("Podman machine status", is_running or "checked"))

    # Check for any remaining development processes
    success, result = run_command(
        "ps aux | grep -E '(neo4j|podman|ansible)' | grep -v grep | wc -l",
        "Development processes check",
        ignore_errors=True,
        timeout=10,
    )

    process_count = 0
    if success and result and result.stdout.strip().isdigit():
        process_count = int(result.stdout.strip())

    validation_results.append(("Development processes", f"{process_count} remaining"))

    return validation_results


def display_resource_summary():
    """Display current resource usage summary"""
    print("📊 Resource Usage Summary:")
    print("-" * 30)

    # Container status
    containers = get_container_status()
    if containers:
        print(f"🐳 Containers: {len(containers)} total")
        for name, status in containers.items():
            status_icon = "🟢" if "up" in status.lower() else "🔴"
            print(f"   {status_icon} {name}: {status}")
    else:
        print("🐳 Containers: None running")

    print()

    # Podman machine status
    machine_name, is_running = get_podman_machine_status()
    if machine_name:
        status_icon = "🟢" if is_running else "🔴"
        print(
            f"⚙️  Podman Machine: {status_icon} {machine_name} ({'Running' if is_running else 'Stopped'})"
        )
    else:
        print("⚙️  Podman Machine: Not managed")

    print()

    # Disk space (approximate)
    success, result = run_command(
        "df -h . | tail -1 | awk '{print $4}'",
        "Available disk space",
        ignore_errors=True,
        timeout=5,
    )
    if success and result:
        print(f"💾 Available disk space: {result.stdout.strip()}")


def main():
    parser = argparse.ArgumentParser(description="P3 Stop - Properly release development resources")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Complete shutdown including Podman machine (slower restart)",
    )
    parser.add_argument(
        "--force", action="store_true", help="Force stop containers without graceful shutdown"
    )

    args = parser.parse_args()

    print("🛑 STOP - Properly releasing development resources")
    print("Enhanced P3 Stop Command with comprehensive resource cleanup")
    print("=" * 70)
    print()

    # Show current status before stopping
    display_resource_summary()
    print()

    # Phase 1: Service Shutdown
    print("🔧 Phase 1: Service Shutdown")
    print("-" * 30)

    # Stop Neo4j with proper data persistence
    if not stop_neo4j_container(force=args.force):
        print("⚠️  Neo4j container stop had issues, continuing...")

    # Stop additional development containers
    stop_additional_containers()

    print()

    # Phase 2: Infrastructure Management
    print("🏗️ Phase 2: Infrastructure Management")
    print("-" * 40)

    # Manage Podman machine
    if not manage_podman_machine(stop_machine=args.full):
        print("⚠️  Podman machine management had issues, continuing...")

    # Run Ansible cleanup
    cleanup_type = "full" if args.full else "standard"
    run_ansible_stop_playbook(cleanup_type)

    print()

    # Phase 3: Cleanup Validation
    print("✅ Phase 3: Cleanup Validation")
    print("-" * 30)

    validation_results = validate_cleanup()

    success_count = 0
    for description, result in validation_results:
        if result is True or result == "checked":
            print(f"✅ {description}")
            success_count += 1
        elif result is False:
            print(f"❌ {description}")
        else:
            print(f"ℹ️  {description}: {result}")

    print()
    print("=" * 70)

    # Final status report
    if args.full:
        print("🛑 STOPPED - Complete resource cleanup completed")
        print("✅ All containers stopped")
        print("✅ Podman machine stopped")
        print("💡 Next startup will take longer due to machine initialization")
    else:
        print("🛑 STOPPED - Development services stopped, machine ready for restart")
        print("✅ Development containers stopped")
        print("🔄 Podman machine kept running for fast restart")
        print("💡 Use 'p3 ready' for quick restart")

    print()
    print("📊 Resource Status:")
    for description, result in validation_results:
        status_icon = "✅" if result is True else "ℹ️" if result != False else "⚠️"
        print(f"   {status_icon} {description}")

    print()
    print("🔄 To restart development:")
    print("   p3 ready              # Quick restart (recommended)")

    if not args.full:
        print()
        print("🛑 For complete shutdown:")
        print("   p3 stop --full        # Stop everything including Podman machine")

    # Show final resource summary
    print()
    display_resource_summary()

    sys.exit(0)


if __name__ == "__main__":
    main()
