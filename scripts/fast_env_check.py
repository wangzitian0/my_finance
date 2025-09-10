#!/usr/bin/env python3
"""
Fast Environment Check - Quick fail detection
Checks critical services in 5 seconds or less, fails fast with clear messages
"""

import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError


def check_podman_machine():
    """Check Podman machine status - 2 second timeout"""
    try:
        result = subprocess.run(
            ["podman", "machine", "list"], capture_output=True, text=True, timeout=2
        )
        if "Currently running" in result.stdout:
            return True, "Podman machine running"
        else:
            return False, f"Podman machine not running properly"
    except subprocess.TimeoutExpired:
        return False, "Podman machine check timed out (2s)"
    except Exception as e:
        return False, f"Podman check failed: {e}"


def check_neo4j_web():
    """Check Neo4j web interface - 3 second timeout"""
    try:
        import socket
        import urllib.request

        # Set socket timeout
        socket.setdefaulttimeout(3)

        req = urllib.request.Request("http://localhost:7474")
        response = urllib.request.urlopen(req, timeout=3)
        if response.status == 200:
            return True, "Neo4j web interface responding"
        else:
            return False, f"Neo4j returned status {response.status}"
    except Exception as e:
        return False, f"Neo4j not accessible: {e}"


def check_pandas_import():
    """Check pandas import - 2 second timeout"""
    try:
        # First try pixi environment
        result = subprocess.run(
            ["pixi", "run", "python", "-c", "import pandas; print('OK')"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and "OK" in result.stdout:
            return True, "pandas import working (pixi)"

        # If pixi fails, try direct python (for test commands)
        result = subprocess.run(
            ["python", "-c", "import pandas; print('OK')"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and "OK" in result.stdout:
            return True, "pandas import working (direct python)"
        else:
            return False, f"pandas import failed in both pixi and direct python"
    except subprocess.TimeoutExpired:
        return False, "pandas import timed out (2s)"
    except Exception as e:
        return False, f"pandas check failed: {e}"


def main():
    """Run all checks in parallel with 5-second total timeout"""
    print("🚀 Fast Environment Check (5s timeout)")
    print("=" * 50)

    start_time = time.time()

    checks = [
        ("Podman Machine", check_podman_machine),
        ("Neo4j Web", check_neo4j_web),
        ("Pandas Import", check_pandas_import),
    ]

    results = {}

    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all checks
            future_to_check = {executor.submit(check_func): name for name, check_func in checks}

            # Wait for results with 5s timeout
            for future in future_to_check:
                try:
                    check_name = future_to_check[future]
                    success, message = future.result(timeout=2)  # Individual 2s timeout
                    results[check_name] = (success, message)

                    status = "✅" if success else "❌"
                    print(f"{status} {check_name}: {message}")

                except TimeoutError:
                    check_name = future_to_check[future]
                    results[check_name] = (False, "Check timed out")
                    print(f"⏰ {check_name}: Check timed out")

    except Exception as e:
        print(f"💥 Check executor failed: {e}")
        sys.exit(1)

    elapsed = time.time() - start_time
    print(f"\n⏱️  Total time: {elapsed:.1f}s")

    # Analyze results
    failed_checks = [name for name, (success, _) in results.items() if not success]

    if failed_checks:
        print(f"\n🚨 {len(failed_checks)} checks failed:")
        for check_name in failed_checks:
            _, message = results[check_name]
            print(f"   • {check_name}: {message}")

        print(f"\n🔧 Quick fixes:")
        if "Podman Machine" in failed_checks:
            print("   • Run: podman machine start")
        if "Neo4j Web" in failed_checks:
            print("   • Run: ansible-playbook infra/ansible/start.yml")
        if "Pandas Import" in failed_checks:
            print("   • Run: pixi install")

        sys.exit(1)
    else:
        print(f"\n✅ All checks passed! Environment ready.")
        sys.exit(0)


if __name__ == "__main__":
    main()
