#!/usr/bin/env python3
"""
Production Readiness Assessment
Phase 3 Infrastructure Integration - Final Deployment Readiness Report
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def run_check(cmd, description, timeout=30):
    """Run a check command and return result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {
            "passed": result.returncode == 0,
            "output": result.stdout.strip() if result.stdout else "",
            "error": result.stderr.strip() if result.stderr else "",
            "duration": 0,  # Will be set by caller
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "output": "", "error": "Timeout", "duration": timeout}
    except Exception as e:
        return {"passed": False, "output": "", "error": str(e), "duration": 0}


def assess_infrastructure():
    """Assess infrastructure readiness for production deployment."""
    print("🎯 PRODUCTION READINESS ASSESSMENT")
    print("=" * 60)
    print("Phase 3 Infrastructure Integration - Final Deployment Report")
    print()

    assessment = {
        "timestamp": time.time(),
        "version": "Phase 3 - Final Integration",
        "categories": {},
    }

    # Category 1: Core Infrastructure
    print("🏗️  1. CORE INFRASTRUCTURE")
    print("-" * 40)

    core_checks = [
        ("python --version", "Python Runtime"),
        ("git --version", "Git Version Control"),
        ("pixi --version", "Pixi Package Manager"),
        ("podman --version", "Podman Container Engine"),
        ("test -f p3.py", "P3 CLI System"),
        ("test -f pixi.toml", "Project Configuration"),
    ]

    core_results = {}
    core_passed = 0

    for cmd, desc in core_checks:
        start_time = time.time()
        result = run_check(cmd, desc)
        result["duration"] = time.time() - start_time
        core_results[desc] = result

        if result["passed"]:
            print(f"✅ {desc}: OK")
            core_passed += 1
        else:
            print(f"❌ {desc}: FAILED - {result['error']}")

    core_score = (core_passed / len(core_checks)) * 100
    assessment["categories"]["core_infrastructure"] = {
        "score": core_score,
        "passed": core_passed,
        "total": len(core_checks),
        "results": core_results,
    }

    print(f"\n📊 Core Infrastructure Score: {core_score:.1f}% ({core_passed}/{len(core_checks)})")

    # Category 2: Neo4j Database System
    print("\n🗄️  2. NEO4J DATABASE SYSTEM")
    print("-" * 40)

    neo4j_checks = [
        ("podman ps | grep neo4j-finance", "Neo4j Container Status"),
        ("curl -s http://localhost:7474 -o /dev/null", "Neo4j Web Interface"),
        ("curl -s http://localhost:7687 -o /dev/null", "Neo4j Database Port"),
        ("test -f infra/docker/neo4j-ci.docker-compose.yml", "Neo4j Configuration"),
    ]

    neo4j_results = {}
    neo4j_passed = 0

    for cmd, desc in neo4j_checks:
        start_time = time.time()
        result = run_check(cmd, desc)
        result["duration"] = time.time() - start_time
        neo4j_results[desc] = result

        if result["passed"]:
            print(f"✅ {desc}: OK")
            neo4j_passed += 1
        else:
            print(f"❌ {desc}: FAILED - {result['error']}")

    neo4j_score = (neo4j_passed / len(neo4j_checks)) * 100
    assessment["categories"]["neo4j_database"] = {
        "score": neo4j_score,
        "passed": neo4j_passed,
        "total": len(neo4j_checks),
        "results": neo4j_results,
    }

    print(f"\n📊 Neo4j Database Score: {neo4j_score:.1f}% ({neo4j_passed}/{len(neo4j_checks)})")

    # Category 3: P3 Workflow System
    print("\n🚀 3. P3 WORKFLOW SYSTEM")
    print("-" * 40)

    p3_checks = [
        ("test -f infra/run_test.py", "P3 Test Runner"),
        ("test -f infra/development/workflow_check.py", "P3 Check Command"),
        ("test -f infra/system/workflow_ready.py", "P3 Ready Command"),
        ("test -f infra/system/env_validation.py", "Environment Validation"),
        ("python p3.py version", "P3 Version Command"),
    ]

    p3_results = {}
    p3_passed = 0

    for cmd, desc in p3_checks:
        start_time = time.time()
        result = run_check(cmd, desc, timeout=10)
        result["duration"] = time.time() - start_time
        p3_results[desc] = result

        if result["passed"]:
            print(f"✅ {desc}: OK")
            p3_passed += 1
        else:
            print(f"❌ {desc}: FAILED - {result['error']}")

    p3_score = (p3_passed / len(p3_checks)) * 100
    assessment["categories"]["p3_workflow"] = {
        "score": p3_score,
        "passed": p3_passed,
        "total": len(p3_checks),
        "results": p3_results,
    }

    print(f"\n📊 P3 Workflow Score: {p3_score:.1f}% ({p3_passed}/{len(p3_checks)})")

    # Category 4: SSOT Configuration System
    print("\n⚙️  4. SSOT CONFIGURATION SYSTEM")
    print("-" * 40)

    ssot_checks = [
        ("test -f common/core/directory_manager.py", "DirectoryManager SSOT"),
        ("test -f common/config/directory_structure.yml", "Directory Configuration"),
        ("test -d common/config/stock_lists", "Stock List Configs"),
        ("test -f common/config/stock_lists/f2.yml", "F2 Scope Config"),
        ("test -f common/config/stock_lists/m7.yml", "M7 Scope Config"),
        ("python common/tests/run_tests.py", "SSOT Compliance Tests"),
    ]

    ssot_results = {}
    ssot_passed = 0

    for cmd, desc in ssot_checks:
        start_time = time.time()
        result = run_check(cmd, desc, timeout=60)
        result["duration"] = time.time() - start_time
        ssot_results[desc] = result

        if result["passed"]:
            print(f"✅ {desc}: OK")
            ssot_passed += 1
        else:
            print(f"❌ {desc}: FAILED - {result['error']}")

    ssot_score = (ssot_passed / len(ssot_checks)) * 100
    assessment["categories"]["ssot_configuration"] = {
        "score": ssot_score,
        "passed": ssot_passed,
        "total": len(ssot_checks),
        "results": ssot_results,
    }

    print(f"\n📊 SSOT Configuration Score: {ssot_score:.1f}% ({ssot_passed}/{len(ssot_checks)})")

    # Category 5: Performance & Scalability
    print("\n⚡ 5. PERFORMANCE & SCALABILITY")
    print("-" * 40)

    perf_checks = [
        ("test -d build_data", "Build Data Structure"),
        ("df -h | grep -E '(/$|/Users)'", "Disk Space Availability"),
        ("python infra/system/env_validation.py", "Quick Environment Validation"),
    ]

    perf_results = {}
    perf_passed = 0

    for cmd, desc in perf_checks:
        start_time = time.time()
        result = run_check(cmd, desc, timeout=60)
        result["duration"] = time.time() - start_time
        perf_results[desc] = result

        if result["passed"]:
            print(f"✅ {desc}: OK")
            perf_passed += 1
        else:
            print(f"❌ {desc}: FAILED - {result['error']}")

    perf_score = (perf_passed / len(perf_checks)) * 100
    assessment["categories"]["performance"] = {
        "score": perf_score,
        "passed": perf_passed,
        "total": len(perf_checks),
        "results": perf_results,
    }

    print(f"\n📊 Performance Score: {perf_score:.1f}% ({perf_passed}/{len(perf_checks)})")

    # Overall Assessment
    print("\n" + "=" * 60)

    category_scores = [
        assessment["categories"]["core_infrastructure"]["score"],
        assessment["categories"]["neo4j_database"]["score"],
        assessment["categories"]["p3_workflow"]["score"],
        assessment["categories"]["ssot_configuration"]["score"],
        assessment["categories"]["performance"]["score"],
    ]

    overall_score = sum(category_scores) / len(category_scores)
    assessment["overall_score"] = overall_score

    total_passed = sum(cat["passed"] for cat in assessment["categories"].values())
    total_checks = sum(cat["total"] for cat in assessment["categories"].values())

    print(f"🎯 OVERALL PRODUCTION READINESS: {overall_score:.1f}%")
    print(f"📊 Total Checks: {total_passed}/{total_checks}")

    # Deployment Recommendation
    if overall_score >= 95:
        status = "READY"
        recommendation = "System is ready for immediate production deployment!"
        deployment_risk = "LOW"
    elif overall_score >= 85:
        status = "MOSTLY_READY"
        recommendation = "System is mostly ready. Address minor issues before deployment."
        deployment_risk = "LOW-MEDIUM"
    elif overall_score >= 75:
        status = "NEEDS_ATTENTION"
        recommendation = "System needs attention before production deployment."
        deployment_risk = "MEDIUM"
    else:
        status = "NOT_READY"
        recommendation = "System is not ready for production deployment."
        deployment_risk = "HIGH"

    assessment["status"] = status
    assessment["recommendation"] = recommendation
    assessment["deployment_risk"] = deployment_risk

    print(f"\n🏷️  Status: {status}")
    print(f"💡 Recommendation: {recommendation}")
    print(f"⚠️  Deployment Risk: {deployment_risk}")

    # Save assessment report
    report_file = Path("build_data/logs/production_readiness.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(report_file, "w") as f:
            json.dump(assessment, f, indent=2)
        print(f"\n📋 Assessment report saved: {report_file}")
    except Exception as e:
        print(f"⚠️  Could not save assessment: {e}")

    # Return appropriate exit code
    if status in ["READY", "MOSTLY_READY"]:
        return 0
    else:
        return 1


def main():
    """Main assessment function."""
    start_time = time.time()

    try:
        exit_code = assess_infrastructure()
        duration = time.time() - start_time

        print(f"\n⏱️  Assessment completed in {duration:.1f}s")

        return exit_code

    except KeyboardInterrupt:
        print("\n⚠️  Assessment interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Assessment failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
