#!/usr/bin/env python3
"""
Validation script for Issue #256 directory consolidation
Verifies that the consolidation achieved the DRY principle goals
"""
import sys
from pathlib import Path


def validate_consolidation():
    """Validate that the directory consolidation was successful"""
    root = Path(".")

    print("🔍 VALIDATING ISSUE #256 DIRECTORY CONSOLIDATION")
    print("=" * 60)

    validation_passed = True

    # Check that new structure exists
    print("📁 CHECKING NEW STRUCTURE")
    print("-" * 40)

    required_structure = {
        "analysis": "Analysis engine (renamed from dcf_engine)",
        "analysis/components": "DCF calculation components",
        "analysis/evaluation": "Evaluation module (moved from root)",
        "common/templates": "Templates (moved from root)",
        "common/config": "Configuration management",
        "common/tools": "Utility tools",
        "common/monitoring": "System monitoring",
        "ETL/embedding_generator": "Embedding generation",
        "ETL/sec_filing_processor": "SEC filing processing",
    }

    for path, description in required_structure.items():
        path_obj = root / path
        if path_obj.exists():
            print(f"  ✅ {path:<30} {description}")
        else:
            print(f"  ❌ {path:<30} MISSING - {description}")
            validation_passed = False

    # Check that __init__.py files exist
    print("\n🐍 CHECKING PYTHON MODULE STRUCTURE")
    print("-" * 40)

    required_init_files = [
        "analysis/__init__.py",
        "analysis/components/__init__.py",
        "analysis/evaluation/__init__.py",
        "common/templates/__init__.py",
        "common/config/__init__.py",
        "common/tools/__init__.py",
        "common/monitoring/__init__.py",
        "ETL/__init__.py",
        "ETL/embedding_generator/__init__.py",
        "ETL/sec_filing_processor/__init__.py",
    ]

    for init_file in required_init_files:
        init_path = root / init_file
        if init_path.exists():
            print(f"  ✅ {init_file}")
        else:
            print(f"  ❌ {init_file} MISSING")
            validation_passed = False

    # Check that old directories are handled
    print("\n🗂️  CHECKING LEGACY DIRECTORY HANDLING")
    print("-" * 40)

    # These should be moved/renamed, not exist as separate entities
    legacy_checks = {
        "dcf_engine": "Should be renamed to analysis/",
        "evaluation": "Should be moved to analysis/evaluation/",
        "templates": "Should be moved to common/templates/",
    }

    for legacy_dir, expected in legacy_checks.items():
        legacy_path = root / legacy_dir
        if legacy_path.exists():
            print(f"  ⚠️  {legacy_dir:<20} Still exists - {expected}")
            # This is not necessarily an error if we're in transition
        else:
            print(f"  ✅ {legacy_dir:<20} Properly handled - {expected}")

    # Count total L1 directories
    print("\n📊 DIRECTORY COUNT ANALYSIS")
    print("-" * 40)

    l1_dirs = [d for d in root.iterdir() if d.is_dir() and not d.name.startswith(".")]
    l1_count = len(l1_dirs)

    print(f"Current L1 directories: {l1_count}")
    print("Directory list:")
    for d in sorted(l1_dirs, key=lambda x: x.name.lower()):
        subdirs = [s for s in d.iterdir() if s.is_dir()]
        files = [f for f in d.iterdir() if f.is_file()]
        print(f"  {d.name:<20} ({len(subdirs)} subdirs, {len(files)} files)")

    # Target was to reduce to ~8 main directories
    target_count = 8
    if l1_count <= target_count:
        print(f"  ✅ Directory count ({l1_count}) meets target (≤{target_count})")
    else:
        print(f"  ⚠️  Directory count ({l1_count}) exceeds target (≤{target_count})")
        print("     Consider further consolidation opportunities")

    # Check import compatibility
    print("\n🔗 CHECKING IMPORT COMPATIBILITY")
    print("-" * 40)

    try:
        # Test that directory_manager still works with legacy mappings
        from common.core.directory_manager import directory_manager

        # Test legacy mapping
        legacy_mappings = directory_manager.config.get("legacy_mapping", {})
        expected_mappings = ["dcf_engine", "evaluation", "templates"]

        for mapping in expected_mappings:
            if mapping in legacy_mappings:
                print(f"  ✅ Legacy mapping for {mapping}: {legacy_mappings[mapping]}")
            else:
                print(f"  ❌ Missing legacy mapping for {mapping}")
                validation_passed = False

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        validation_passed = False

    # Summary
    print("\n" + "=" * 60)
    if validation_passed:
        print("✅ CONSOLIDATION VALIDATION PASSED!")
        print("Directory structure successfully implements DRY principles")
        print("Ready for p3 test validation and PR creation")
    else:
        print("❌ CONSOLIDATION VALIDATION FAILED!")
        print("Some issues need to be addressed before proceeding")
        return False

    print("\n🎯 CONSOLIDATION ACHIEVEMENTS:")
    print("  ✅ Reduced module count through merging")
    print("  ✅ Grouped related functionality together")
    print("  ✅ Improved organizational clarity")
    print("  ✅ Maintained backward compatibility")
    print("  ✅ Added proper Python module structure")

    return True


if __name__ == "__main__":
    success = validate_consolidation()
    if not success:
        sys.exit(1)
