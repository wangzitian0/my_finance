#!/usr/bin/env python3
"""
Workflow-Oriented Environment Command: READY
"I want to start working" - ensure everything is ready

Replaces 8 commands: env-status, env-start, neo4j-start, status, verify-env, 
podman-status, cache-status, check-integrity
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, ignore_errors=False):
    """Execute command and display results"""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 or ignore_errors:
            print(f"✅ {description} - OK")
            if result.stdout.strip():
                # Only show key information, avoid excessive output
                lines = result.stdout.strip().split('\n')
                for line in lines[:3]:  # Show only first 3 lines
                    if line.strip():
                        print(f"   {line}")
                if len(lines) > 3:
                    print("   ...")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    print("🚀 READY - Getting everything ready for development")
    print("=" * 50)
    
    steps = [
        # 1. Check basic environment
        ("pixi run python --version", "Python environment check", False),
        
        # 2. Start necessary services
        ("podman start neo4j-finance", "Starting Neo4j", True),  # May already be running
        
        # 3. Environment status check
        ("pixi run python infra/comprehensive_env_status.py", "Comprehensive environment status", False),
        
        # 4. Quick package verification
        ("pixi run python -c 'import pandas, numpy, requests; print(\"Core packages OK\")'", "Core packages check", False),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for cmd, desc, ignore_errors in steps:
        if run_command(cmd, desc, ignore_errors):
            success_count += 1
        print()  # Empty line separator
    
    print("=" * 50)
    if success_count == total_steps:
        print("🎉 READY - Everything is set up for development!")
        print("💡 You can now use: p3 build, p3 e2e, p3 create-pr")
        sys.exit(0)
    elif success_count >= total_steps - 1:
        print("⚠️  READY - Mostly ready, minor issues detected")
        print("💡 You can proceed, but consider running 'p3 reset' if issues persist")
        sys.exit(0)
    else:
        print("❌ NOT READY - Major issues detected")
        print("💡 Please run 'p3 reset' to fix environment issues")
        sys.exit(1)


if __name__ == "__main__":
    main()