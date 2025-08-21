#!/usr/bin/env python3
"""
ML Container Management
Builds and manages the sentence-transformers Podman container
"""
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import requests


def run_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command with error handling"""
    print(f"🔧 Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_podman() -> bool:
    """Check if Podman is available and running"""
    try:
        result = run_command(["podman", "info"], check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Podman not found. Please install Podman first.")
        return False


def build_container():
    """Build the sentence-transformers container"""
    print("🏗️ Building sentence-transformers container...")

    infra_dir = Path(__file__).parent
    project_root = infra_dir.parent

    # Copy the service script to build context
    dockerfile_path = infra_dir / "sentence-transformers.Dockerfile"
    service_script = infra_dir / "sentence_transformers_service.py"

    if not dockerfile_path.exists():
        print(f"❌ Dockerfile not found: {dockerfile_path}")
        sys.exit(1)

    if not service_script.exists():
        print(f"❌ Service script not found: {service_script}")
        sys.exit(1)

    # Build the container
    build_cmd = [
        "podman",
        "build",
        "-f",
        str(dockerfile_path),
        "-t",
        "my-finance-ml:latest",
        str(infra_dir),
    ]

    run_command(build_cmd)
    print("✅ Container built successfully")


def start_container():
    """Start the ML service container"""
    print("🚀 Starting ML service container...")

    # Stop existing container if running
    run_command(["podman", "stop", "ml-service"], check=False)
    run_command(["podman", "rm", "ml-service"], check=False)

    # Start new container
    run_cmd = [
        "podman",
        "run",
        "-d",
        "--name",
        "ml-service",
        "-p",
        "8888:8888",
        "--restart",
        "always",
        "my-finance-ml:latest",
    ]

    run_command(run_cmd)

    # Wait for service to start
    print("⏳ Waiting for service to start...")
    for i in range(30):  # 30 second timeout
        try:
            response = requests.get("http://localhost:8888/health", timeout=2)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ ML service started successfully!")
                print(f"   Status: {health_data.get('status')}")
                print(f"   ML Available: {health_data.get('ml_available')}")
                print(f"   Model: {health_data.get('model_info')}")
                return
        except requests.RequestException:
            pass

        time.sleep(1)

    print("⚠️ Service may not be fully ready. Check with: podman logs ml-service")


def stop_container():
    """Stop the ML service container"""
    print("🛑 Stopping ML service container...")
    run_command(["podman", "stop", "ml-service"], check=False)
    run_command(["podman", "rm", "ml-service"], check=False)
    print("✅ Container stopped")


def status_container():
    """Check container status"""
    print("📊 ML Service Container Status")
    print("=" * 50)

    # Check container status
    result = run_command(["podman", "ps", "-a", "--filter", "name=ml-service"], check=False)

    # Check service health
    try:
        response = requests.get("http://localhost:8888/health", timeout=2)
        if response.status_code == 200:
            health_data = response.json()
            print(f"🌐 Service Health:")
            print(f"   Status: {health_data.get('status')}")
            print(f"   ML Available: {health_data.get('ml_available')}")
            print(f"   Model Loaded: {health_data.get('model_loaded')}")
            print(f"   Model: {health_data.get('model_info')}")
        else:
            print(f"⚠️ Service responded with status: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Service not accessible: {e}")


def test_service():
    """Test the ML service"""
    print("🧪 Testing ML service...")

    try:
        # Test encoding
        test_data = {"texts": ["Hello world", "Testing sentence transformers"]}

        response = requests.post("http://localhost:8888/encode", json=test_data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Encoding test passed!")
            print(f"   Encoded {result.get('count')} texts")
            print(f"   Embedding dimension: {result.get('dimension')}")
        else:
            print(f"❌ Encoding test failed: {response.status_code}")
            print(response.text)

    except requests.RequestException as e:
        print(f"❌ Service test failed: {e}")


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python manage_ml_container.py {build|start|stop|status|test|restart}")
        sys.exit(1)

    action = sys.argv[1].lower()

    if not check_podman():
        sys.exit(1)

    if action == "build":
        build_container()
    elif action == "start":
        start_container()
    elif action == "stop":
        stop_container()
    elif action == "status":
        status_container()
    elif action == "test":
        test_service()
    elif action == "restart":
        stop_container()
        time.sleep(2)
        start_container()
    else:
        print(f"❌ Unknown action: {action}")
        print("Available actions: build, start, stop, status, test, restart")
        sys.exit(1)


if __name__ == "__main__":
    main()
