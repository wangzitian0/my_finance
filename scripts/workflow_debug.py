#!/usr/bin/env python3
"""
Workflow-Oriented Command: DEBUG
"Diagnose issues" - unified status check
"""

import subprocess
import sys
from pathlib import Path


def run_check(cmd, description):
    """Run diagnostic check."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            if result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                for line in lines[:5]:  # Show first 5 lines
                    print(f"   {line}")
                if len(lines) > 5:
                    print("   ...")
        else:
            print(f"❌ {description} - ISSUE DETECTED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")


def main():
    print("🔍 DEBUG - Diagnosing environment issues")
    print("=" * 50)

    checks = [
        # Environment checks
        ("pixi --version", "Pixi installation"),
        ("pixi run python --version", "Python environment"),
        ("pixi run python -c 'import pandas, numpy; print(\"Core packages OK\")'", "Core packages"),
        # Service checks
        ("podman ps --format 'table {{.Names}}\t{{.Status}}'", "Container status"),
        ("podman logs neo4j-finance --tail 5 2>/dev/null", "Neo4j logs"),
        # Git checks
        ("git status --short", "Git status"),
        ("git branch --show-current", "Current branch"),
        # Build checks
        ("ls -la build_data/stage_04_query_results/ 2>/dev/null | head -5", "Build outputs"),
        # Worktree checks
        ("pwd", "Current directory"),
        ("ls -la .pixi/envs/default/bin/python 2>/dev/null", "Worktree Python"),
    ]

    for cmd, desc in checks:
        run_check(cmd, desc)
        print()

    print("=" * 50)
    print("💡 DEBUG COMPLETE - Review issues above")
    print("💡 If issues found, run 'p3 reset' to fix environment")


if __name__ == "__main__":
    main()
