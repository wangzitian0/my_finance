#!/usr/bin/env python3
"""
Script to replace 'pixi run' calls with 'p3' equivalents throughout the codebase.
This enforces the use of our unified p3 CLI instead of direct pixi calls.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Mapping of pixi run commands to p3 equivalents
COMMAND_MAPPING = {
    # Environment commands
    "p3 env setup": "p3 env setup",
    "p3 env start": "p3 env start",
    "p3 env stop": "p3 env stop",
    "p3 env status": "p3 env status",
    "p3 env reset": "p3 env reset",
    # Container commands
    "p3 podman status": "p3 podman status",
    "p3 neo4j logs": "p3 neo4j logs",
    "p3 neo4j connect": "p3 neo4j connect",
    "p3 neo4j restart": "p3 neo4j restart",
    "p3 neo4j stop": "p3 neo4j stop",
    "p3 neo4j start": "p3 neo4j start",
    # Development commands
    "p3 format": "p3 format",
    "p3 lint": "p3 lint",
    "p3 typecheck": "p3 typecheck",
    "p3 test": "p3 test",
    "p3 test-e2e": "p3 e2e",
    # Build commands
    "p3 build run f2": "p3 build run f2",
    "p3 build run m7": "p3 build run m7",
    "p3 build run": "p3 build run",
    "p3 build run n100": "p3 build run n100",
    "p3 build run n100": "p3 build run n100",
    "p3 build run v3k": "p3 build run v3k",
    "p3 build run v3k": "p3 build run v3k",
    "p3 build-status": "p3 build-status",
    "p3 create-build": "p3 create-build",
    "p3 release-build": "p3 release-build",
    # Workflow commands
    "p3 create-pr": "p3 create-pr",
    "p3 commit-data-changes": "p3 commit-data-changes",
    "p3 cleanup-branches": "p3 cleanup-branches",
    "p3 cleanup-branches-dry-run": "p3 cleanup-branches --dry-run",
    "p3 cleanup-branches-auto": "p3 cleanup-branches --auto",
    "p3 shutdown-all": "p3 shutdown-all",
    # Status commands
    "p3 status": "p3 status",
    "p3 cache-status": "p3 cache-status",
    "p3 verify-env": "p3 verify-env",
    "p3 check-integrity": "p3 check-integrity",
    # E2E testing variants
    "p3 e2e": "p3 e2e",
    "p3 e2e f2": "p3 e2e f2",
    "p3 e2e m7": "p3 e2e m7",
    "p3 e2e n100": "p3 e2e n100",
    "p3 e2e v3k": "p3 e2e v3k",
}


def find_files_to_process() -> List[Path]:
    """Find all files that should be processed for pixi run replacements"""
    project_root = Path(__file__).parent.parent

    # File patterns to include
    patterns = ["**/*.py", "**/*.md", "**/*.yml", "**/*.yaml", "**/*.sh", "**/*.txt"]

    # Directories to exclude
    exclude_dirs = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}

    files = []
    for pattern in patterns:
        for file_path in project_root.glob(pattern):
            # Skip if file is in excluded directory
            if any(exc_dir in file_path.parts for exc_dir in exclude_dirs):
                continue

            # Skip binary files and large data files
            if file_path.suffix in {".json", ".log", ".png", ".jpg", ".pdf"}:
                continue

            if file_path.is_file():
                files.append(file_path)

    return files


def process_file(file_path: Path) -> Tuple[int, List[str]]:
    """Process a single file and return number of replacements made"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return 0, []

    original_content = content
    replacements_made = []

    # Apply each mapping
    for old_cmd, new_cmd in COMMAND_MAPPING.items():
        if old_cmd in content:
            # Count occurrences before replacement
            count = content.count(old_cmd)
            content = content.replace(old_cmd, new_cmd)
            if count > 0:
                replacements_made.append(f"{old_cmd} -> {new_cmd} ({count} times)")

    # Only write if changes were made
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    return len(replacements_made), replacements_made


def main():
    """Main function to process all files"""
    print("🔧 Fixing 'pixi run' calls throughout codebase...")
    print("   Replacing with unified 'p3' command equivalents")
    print()

    files = find_files_to_process()
    print(f"📁 Found {len(files)} files to process")

    total_files_changed = 0
    total_replacements = 0
    detailed_changes = []

    for file_path in files:
        replacement_count, replacements = process_file(file_path)

        if replacement_count > 0:
            total_files_changed += 1
            total_replacements += replacement_count

            # Show detailed changes for important files
            rel_path = file_path.relative_to(Path(__file__).parent.parent)
            detailed_changes.append((str(rel_path), replacements))

            print(f"✅ {rel_path}: {replacement_count} replacements")

    print()
    print("📊 Summary:")
    print(f"   Files processed: {len(files)}")
    print(f"   Files changed: {total_files_changed}")
    print(f"   Total replacements: {total_replacements}")

    if detailed_changes:
        print()
        print("🔍 Detailed changes:")
        for file_path, replacements in detailed_changes[:10]:  # Show first 10
            print(f"   {file_path}:")
            for replacement in replacements[:5]:  # Show first 5 per file
                print(f"     • {replacement}")
            if len(replacements) > 5:
                print(f"     • ... and {len(replacements) - 5} more")

        if len(detailed_changes) > 10:
            print(f"   ... and {len(detailed_changes) - 10} more files")

    print()
    print("✅ All 'pixi run' calls have been updated to use 'p3' commands!")
    print("   The codebase now consistently uses the unified CLI.")


if __name__ == "__main__":
    main()
