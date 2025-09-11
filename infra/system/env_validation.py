#!/usr/bin/env python3
"""
Infrastructure Environment Validation
Quick validation for Phase 3 infrastructure integration
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def quick_check(cmd, description, timeout=10):
    """Quick command check with minimal output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0
    except:
        return False


def validate_infrastructure():
    """Validate core infrastructure components."""
    print("🔍 Infrastructure Validation - Phase 3 Integration")
    print("=" * 50)

    # Core infrastructure checks
    checks = [
        # System basics
        ("python --version", "Python availability"),
        ("git --version", "Git availability"),
        ("which pixi", "Pixi installation"),
        # Container infrastructure
        ("podman version", "Podman installation"),
        ("podman ps", "Podman services"),
        ("curl -s http://localhost:7474 -o /dev/null", "Neo4j web interface"),
        ("curl -s http://localhost:7687 -o /dev/null", "Neo4j database port"),
        # P3 system files
        ("test -f p3.py", "P3 CLI exists"),
        ("test -f infra/run_test.py", "Test runner exists"),
        ("test -f common/core/directory_manager.py", "DirectoryManager exists"),
        # Configuration files
        ("test -f pixi.toml", "Pixi configuration"),
        ("test -f common/config/directory_structure.yml", "Directory config"),
        # Build data structure
        ("test -d build_data", "Build data directory"),
        ("test -d common/config", "Common config directory"),
    ]

    passed = 0
    total = len(checks)

    for cmd, desc in checks:
        if quick_check(cmd, desc):
            print(f"✅ {desc}")
            passed += 1
        else:
            print(f"❌ {desc}")

    print(f"\n📊 Infrastructure Status: {passed}/{total} ({(passed/total)*100:.1f}%)")

    # P3 command availability
    print("\n🚀 P3 Command Availability")
    print("-" * 30)

    p3_commands = ["ready", "check", "test", "ship", "debug", "reset", "build", "version"]
    p3_working = 0

    for cmd in p3_commands:
        if quick_check(f"python p3.py {cmd} --help", f"p3 {cmd}"):
            print(f"✅ p3 {cmd}")
            p3_working += 1
        else:
            print(f"❌ p3 {cmd}")

    print(
        f"\n📊 P3 Commands: {p3_working}/{len(p3_commands)} ({(p3_working/len(p3_commands))*100:.1f}%)"
    )

    # Overall assessment
    overall_score = (passed + p3_working) / (total + len(p3_commands)) * 100

    print(f"\n🎯 Overall Infrastructure Score: {overall_score:.1f}%")

    if overall_score >= 90:
        print("🎉 INFRASTRUCTURE READY - Phase 3 integration successful!")
        return 0
    elif overall_score >= 75:
        print("⚠️  INFRASTRUCTURE MOSTLY READY - Minor issues detected")
        return 0
    else:
        print("❌ INFRASTRUCTURE NOT READY - Significant issues found")
        return 1


def validate_configurations():
    """Validate configuration integration."""
    print("\n⚙️  Configuration Validation")
    print("-" * 30)

    config_files = [
        "common/config/directory_structure.yml",
        "common/config/stock_lists/f2.yml",
        "common/config/stock_lists/m7.yml",
        "pixi.toml",
    ]

    config_score = 0
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ {config_file}")
            config_score += 1
        else:
            print(f"❌ {config_file}")

    print(f"\n📊 Configuration Files: {config_score}/{len(config_files)}")

    return config_score >= len(config_files) * 0.8  # 80% threshold


def main():
    """Main validation function."""
    start_time = time.time()

    # Core infrastructure validation
    infra_status = validate_infrastructure()

    # Configuration validation
    config_ok = validate_configurations()

    duration = time.time() - start_time

    # Summary
    print("\n" + "=" * 50)
    print(f"🎯 PHASE 3 INTEGRATION VALIDATION COMPLETE ({duration:.1f}s)")

    if infra_status == 0 and config_ok:
        print("✅ Infrastructure integration successful!")
        print("🚀 System ready for P3 workflow testing")
        return 0
    else:
        print("⚠️  Infrastructure integration needs attention")
        print("💡 Review errors above before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())
