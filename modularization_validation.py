#!/usr/bin/env python3
"""
Modularization Validation Script for Issue #256 Phase 2

This script validates the L1/L2 module structure improvements.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from common.utils.module_validation import generate_validation_report, validate_module_structure


def main():
    print("Issue #256 Phase 2: L1/L2 Modularization Validation")
    print("=" * 60)

    # Run validation
    results = validate_module_structure()

    # Generate and print report
    report = generate_validation_report(results)
    print(report)

    # Summary of changes made
    print("\nChanges Made in Phase 2:")
    print("-" * 30)

    created_files = [
        "evaluation/__init__.py",
        "ETL/sec_filing_processor/__init__.py",
        "ETL/embedding_generator/__init__.py",
        "dcf_engine/components/__init__.py",
        "common/config/__init__.py",
        "common/build/__init__.py",
        "common/monitoring/__init__.py",
        "infra/data/__init__.py",
        "templates/__init__.py",
    ]

    updated_files = [
        "ETL/__init__.py",
        "common/schemas/__init__.py",
        "common/agents/__init__.py",
        "infra/git/__init__.py",
        "infra/hrbp/__init__.py",
        "infra/p3/__init__.py",
        "infra/development/__init__.py",
        "common/utils/__init__.py",
    ]

    print(f"✅ Created {len(created_files)} new __init__.py files")
    print(f"✅ Updated {len(updated_files)} existing __init__.py files")
    print(f"✅ Added module_validation.py utility for ongoing validation")

    # Check completion status
    summary = results["validation_summary"]
    total = results["total_packages"]
    success_rate = (summary["passed"] / total) * 100 if total > 0 else 0

    print(f"\nModularization Success Rate: {success_rate:.1f}%")

    if summary["failed"] == 0:
        print("🎉 All packages now have proper module structure!")
        return 0
    else:
        print(f"⚠️  {summary['failed']} packages still need attention")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
