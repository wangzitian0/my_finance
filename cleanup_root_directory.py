#!/usr/bin/env python3
"""
Issue #256 Directory Structure Adjustment Phase 1: Clean Root Directory
EXECUTE directory cleanup operations using directory_manager SSOT patterns.
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple

# Import directory manager for SSOT compliance
from common.core.directory_manager import directory_manager, get_config_path


def analyze_root_directory() -> Tuple[List[Path], List[Path], List[Path], List[Path]]:
    """Analyze current root directory structure and categorize files"""
    root_path = directory_manager.root_path

    # File categories to identify
    coverage_files = []
    test_files = []
    config_files = []
    other_files = []

    print(f"Analyzing root directory: {root_path}")
    print("=" * 60)

    # Get all files in root directory (not subdirectories)
    for item in root_path.iterdir():
        if item.is_file():
            if item.name.startswith(".coverage"):
                coverage_files.append(item)
                print(f"Coverage file: {item.name}")
            elif item.name.startswith("test_") and item.name.endswith(".py.disabled"):
                test_files.append(item)
                print(f"Test file: {item.name}")
            elif (
                item.suffix in [".yml", ".yaml", ".toml", ".ini", ".cfg"]
                and "config" in item.name.lower()
            ):
                config_files.append(item)
                print(f"Config file: {item.name}")
            else:
                other_files.append(item)
                print(f"Other file: {item.name}")

    print("=" * 60)
    print(f"Found {len(coverage_files)} coverage files")
    print(f"Found {len(test_files)} test files")
    print(f"Found {len(config_files)} config files")
    print(f"Found {len(other_files)} other files")
    print("=" * 60)

    return coverage_files, test_files, config_files, other_files


def clean_coverage_files(coverage_files: List[Path]) -> int:
    """Remove all .coverage.* files from root directory"""
    removed_count = 0

    print("Cleaning coverage files...")
    for file in coverage_files:
        try:
            print(f"  Removing: {file.name}")
            file.unlink()
            removed_count += 1
        except Exception as e:
            print(f"  ERROR removing {file.name}: {e}")

    print(f"Removed {removed_count} coverage files")
    return removed_count


def move_test_files(test_files: List[Path]) -> int:
    """Move test_*.py.disabled files to tests/ directory"""
    moved_count = 0

    # Ensure tests directory exists
    tests_dir = directory_manager.root_path / "tests"
    tests_dir.mkdir(exist_ok=True)

    print("Moving test files to tests/ directory...")
    for file in test_files:
        try:
            destination = tests_dir / file.name
            print(f"  Moving: {file.name} -> tests/{file.name}")

            # Check if destination already exists
            if destination.exists():
                print(f"    WARNING: {destination} already exists, adding suffix")
                destination = tests_dir / f"{file.stem}_moved{file.suffix}"

            shutil.move(str(file), str(destination))
            moved_count += 1
        except Exception as e:
            print(f"  ERROR moving {file.name}: {e}")

    print(f"Moved {moved_count} test files")
    return moved_count


def organize_config_files(config_files: List[Path]) -> int:
    """Move standalone config files to common/config/"""
    moved_count = 0

    # Get config directory using directory_manager
    config_dir = get_config_path()
    config_dir.mkdir(parents=True, exist_ok=True)

    print("Organizing config files to common/config/...")
    for file in config_files:
        try:
            destination = config_dir / file.name
            print(f"  Moving: {file.name} -> common/config/{file.name}")

            # Check if destination already exists
            if destination.exists():
                print(f"    WARNING: {destination} already exists, adding suffix")
                destination = config_dir / f"{file.stem}_moved{file.suffix}"

            shutil.move(str(file), str(destination))
            moved_count += 1
        except Exception as e:
            print(f"  ERROR moving {file.name}: {e}")

    print(f"Moved {moved_count} config files")
    return moved_count


def validate_clean_structure() -> Tuple[int, List[str]]:
    """Validate that root directory contains only core modules"""
    root_path = directory_manager.root_path

    # Expected core directories
    core_directories = {
        "ETL",
        "dcf_engine",
        "graph_rag",
        "common",
        "infra",
        "evaluation",
        "templates",
        "build_data",
        "tests",
        ".git",
    }

    # Expected core files (minimal set)
    core_files = {
        "README.md",
        "CLAUDE.md",
        "pyproject.toml",
        "pixi.toml",
        "p3",
        ".gitignore",
        "MIGRATION_SUMMARY.md",
    }

    remaining_files = []
    total_items = 0

    print("Validating clean root directory structure...")
    print("Core directories expected:", sorted(core_directories))
    print("Core files expected:", sorted(core_files))
    print()

    for item in root_path.iterdir():
        total_items += 1
        item_name = item.name

        if item.is_dir():
            if item_name not in core_directories and not item_name.startswith("."):
                remaining_files.append(f"Unexpected directory: {item_name}")
                print(f"  UNEXPECTED DIR: {item_name}")
        elif item.is_file():
            if item_name not in core_files and not item_name.startswith("."):
                remaining_files.append(f"Unexpected file: {item_name}")
                print(f"  UNEXPECTED FILE: {item_name}")

    print(f"\nTotal items in root: {total_items}")
    print(f"Unexpected items: {len(remaining_files)}")

    return total_items, remaining_files


def execute_directory_cleanup():
    """EXECUTE the complete directory cleanup workflow"""
    print("EXECUTING Issue #256 Directory Structure Adjustment Phase 1")
    print("=" * 60)

    # Phase 1: Analyze current structure
    coverage_files, test_files, config_files, other_files = analyze_root_directory()

    total_before = len(coverage_files) + len(test_files) + len(config_files) + len(other_files)
    print(f"\nTotal files to process: {total_before}")

    # Phase 2: Execute cleanup operations
    print("\n" + "=" * 60)
    print("EXECUTING CLEANUP OPERATIONS")
    print("=" * 60)

    removed_coverage = clean_coverage_files(coverage_files)
    moved_tests = move_test_files(test_files)
    moved_configs = organize_config_files(config_files)

    # Phase 3: Validate results
    print("\n" + "=" * 60)
    print("VALIDATION PHASE")
    print("=" * 60)

    total_items, unexpected_items = validate_clean_structure()

    # Phase 4: Summary report
    print("\n" + "=" * 60)
    print("CLEANUP SUMMARY REPORT")
    print("=" * 60)

    total_processed = removed_coverage + moved_tests + moved_configs
    reduction_percent = (total_processed / max(total_before, 1)) * 100

    print(f"Files processed: {total_processed}/{total_before}")
    print(f"Coverage files removed: {removed_coverage}")
    print(f"Test files moved: {moved_tests}")
    print(f"Config files moved: {moved_configs}")
    print(f"File reduction: {reduction_percent:.1f}%")
    print(f"Root directory items remaining: {total_items}")

    if unexpected_items:
        print(f"\nUnexpected items remaining: {len(unexpected_items)}")
        for item in unexpected_items[:10]:  # Show first 10
            print(f"  - {item}")
        if len(unexpected_items) > 10:
            print(f"  ... and {len(unexpected_items) - 10} more")
    else:
        print("\nROOT DIRECTORY STRUCTURE: CLEAN ✅")

    # Success criteria check
    success = (
        removed_coverage >= 15  # Expect at least 15 coverage files removed
        and moved_tests >= 3  # Expect at least 3 test files moved
        and reduction_percent >= 70  # Target 70% reduction achieved
    )

    print(f"\nCLEANUP SUCCESS: {'✅ YES' if success else '❌ NO'}")

    return {
        "total_processed": total_processed,
        "removed_coverage": removed_coverage,
        "moved_tests": moved_tests,
        "moved_configs": moved_configs,
        "reduction_percent": reduction_percent,
        "remaining_items": total_items,
        "unexpected_items": len(unexpected_items),
        "success": success,
    }


if __name__ == "__main__":
    # EXECUTE the directory cleanup
    results = execute_directory_cleanup()

    # Exit with appropriate code
    exit_code = 0 if results["success"] else 1
    exit(exit_code)
