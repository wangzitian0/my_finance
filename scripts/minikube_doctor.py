#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
minikube_doctor.py

Environment doctor script to check Minikube and Kubernetes setup
for cross-platform development.
"""

import os
import shutil
import subprocess
import platform
import sys
from pathlib import Path


def print_status(component, status, message="", details=""):
    """Prints a formatted status line."""
    status_icon = "✅" if status else "❌"
    print(f"[{status_icon}] {component:<20} {message}")
    if details:
        print(f"    {'':<20}   └── {details}")


def check_minikube():
    """Checks if Minikube is installed and running."""
    minikube_executable = shutil.which("minikube")
    if not minikube_executable:
        print_status(
            "Minikube Installed",
            False,
            "Minikube command not found.",
            "Install: 'brew install minikube' (macOS) or see https://minikube.sigs.k8s.io/docs/start/"
        )
        return False
    
    print_status("Minikube Installed", True, f"Found at {minikube_executable}")
    
    # Check if Minikube is running
    try:
        result = subprocess.check_output(["minikube", "status"], stderr=subprocess.STDOUT)
        status_output = result.decode().strip()
        if "Running" in status_output:
            print_status("Minikube Running", True, "Cluster is active")
            return True
        else:
            print_status("Minikube Running", False, "Cluster not running",
                       "Start with: 'minikube start' or 'pixi run k8s-start'")
            return False
    except subprocess.CalledProcessError:
        print_status("Minikube Running", False, "Cluster not running",
                   "Start with: 'minikube start' or 'pixi run k8s-start'")
        return False


def check_kubectl():
    """Checks if kubectl is available."""
    kubectl_executable = shutil.which("kubectl")
    minikube_executable = shutil.which("minikube")
    
    if kubectl_executable:
        print_status("kubectl Available", True, f"Found at {kubectl_executable}")
        kubectl_cmd = "kubectl"
    elif minikube_executable:
        print_status("kubectl Available", True, "Via minikube kubectl")
        kubectl_cmd = "minikube kubectl --"
    else:
        print_status("kubectl Available", False, "kubectl not found",
                   "Install kubectl or use 'minikube kubectl --'")
        return False, None
    
    # Test kubectl connectivity
    try:
        subprocess.check_output(kubectl_cmd.split() + ["cluster-info"], stderr=subprocess.STDOUT)
        print_status("kubectl Connected", True, "Connected to cluster")
        return True, kubectl_cmd
    except subprocess.CalledProcessError:
        print_status("kubectl Connected", False, "Cannot connect to cluster",
                   "Ensure Minikube is running")
        return False, kubectl_cmd


def check_pixi():
    """Checks if Pixi is installed and active."""
    pixi_executable = shutil.which("pixi")
    if not pixi_executable:
        print_status(
            "Pixi Installed",
            False,
            "Pixi command not found.",
            "Install from https://pixi.sh/"
        )
        return False
    
    print_status("Pixi Installed", True, f"Found at {pixi_executable}")
    
    # Check if in Pixi environment
    in_pixi_env = "PIXI_ENV_DIR" in os.environ
    if not in_pixi_env:
        print_status(
            "Pixi Environment",
            False,
            "Not in Pixi shell.",
            "Run 'pixi shell' to activate"
        )
        return False
    
    print_status("Pixi Environment", True, "Pixi shell is active")
    return True


def check_project_structure():
    """Checks if required project files exist."""
    required_items = [
        ("k8s/neo4j.yaml", "Kubernetes Neo4j manifest"),
        ("pixi.toml", "Pixi configuration"),
        ("ansible/init.yml", "Ansible playbook"),
    ]
    
    all_good = True
    for item, description in required_items:
        path = Path(item)
        if path.exists():
            print_status("Project Files", True, f"{description} exists")
        else:
            print_status("Project Files", False, f"{description} missing")
            all_good = False
    
    return all_good


def check_neo4j_deployment(kubectl_cmd):
    """Checks if Neo4j is deployed and running in Kubernetes."""
    if not kubectl_cmd:
        return False
    
    try:
        # Check if deployment exists
        subprocess.check_output(
            kubectl_cmd.split() + ["get", "deployment", "neo4j"],
            stderr=subprocess.STDOUT
        )
        print_status("Neo4j Deployed", True, "Deployment exists")
        
        # Check if pods are running
        result = subprocess.check_output(
            kubectl_cmd.split() + ["get", "pods", "-l", "app=neo4j", "-o", "jsonpath='{.items[*].status.phase}'"],
            stderr=subprocess.STDOUT
        )
        pod_status = result.decode().strip().strip("'")
        
        if "Running" in pod_status:
            print_status("Neo4j Running", True, "Pod(s) are running")
            return True
        else:
            print_status("Neo4j Running", False, f"Pod status: {pod_status}",
                       "Check with: 'kubectl get pods -l app=neo4j'")
            return False
            
    except subprocess.CalledProcessError:
        print_status("Neo4j Deployed", False, "Deployment not found",
                   "Deploy with: 'kubectl apply -f k8s/neo4j.yaml'")
        return False


def get_connection_info():
    """Gets Neo4j connection information."""
    try:
        minikube_ip = subprocess.check_output(["minikube", "ip"]).decode().strip()
        print_status("Connection Info", True, f"Minikube IP: {minikube_ip}")
        print(f"    {'Neo4j Web Interface':<20}   └── http://{minikube_ip}:30474")
        print(f"    {'Neo4j Bolt Connection':<20}   └── bolt://{minikube_ip}:30687")
        print(f"    {'Credentials':<20}   └── neo4j / finance123")
        return True
    except subprocess.CalledProcessError:
        print_status("Connection Info", False, "Cannot get Minikube IP")
        return False


def main():
    """Run all environment checks."""
    print("🩺 Running Minikube/Kubernetes environment checks...")
    print("=" * 60)
    
    all_ok = True
    
    # --- Core Tools ---
    minikube_ok = check_minikube()
    if not minikube_ok:
        all_ok = False
    
    kubectl_ok, kubectl_cmd = check_kubectl()
    if not kubectl_ok:
        all_ok = False
    
    pixi_ok = check_pixi()
    if not pixi_ok:
        all_ok = False
    
    # --- Project Structure ---
    print("-" * 60)
    print("Project Structure:")
    
    structure_ok = check_project_structure()
    if not structure_ok:
        all_ok = False
    
    # --- Service Status (only if basic tools work) ---
    if minikube_ok and kubectl_ok:
        print("-" * 60)
        print("Service Status:")
        
        neo4j_ok = check_neo4j_deployment(kubectl_cmd)
        if neo4j_ok:
            get_connection_info()
        else:
            all_ok = False
    
    print("=" * 60)
    
    if all_ok:
        print("✅ Your Minikube environment is ready!")
        print("\nQuick commands:")
        print("- Check cluster: 'pixi run k8s-status'")
        print("- View services: 'pixi run services-status'")
        print("- Connect to Neo4j: 'pixi run neo4j-connect'")
        print("- View logs: 'pixi run neo4j-logs'")
    else:
        print("❌ Some checks failed. Please address the issues above.")
        print("\nCommon fixes:")
        print("1. Install missing tools (Minikube, kubectl)")
        print("2. Start Minikube: 'pixi run k8s-start'")
        print("3. Deploy services: 'pixi run services-deploy'")
        sys.exit(1)


if __name__ == "__main__":
    main()