#!/usr/bin/env python3
"""List all files in root directory for Issue #256 analysis"""

from pathlib import Path


def list_root_files():
    """List all files in the root directory"""
    root_path = Path("/Users/SP14016/zitian/my_finance/.git/worktree/feature-256-dir-adjust")

    print(f"Root directory: {root_path}")
    print("=" * 80)

    # Separate files and directories
    files = []
    directories = []

    try:
        for item in sorted(root_path.iterdir()):
            if item.is_file():
                files.append(item.name)
            elif item.is_dir():
                directories.append(item.name)
    except Exception as e:
        print(f"Error listing directory: {e}")
        return

    print("DIRECTORIES:")
    for d in directories:
        print(f"  {d}/")

    print(f"\nFILES ({len(files)} total):")

    # Categorize files
    coverage_files = [f for f in files if f.startswith(".coverage")]
    test_files = [f for f in files if f.startswith("test_") and f.endswith(".py.disabled")]
    config_files = [
        f
        for f in files
        if any(ext in f for ext in [".yml", ".yaml", ".toml"]) and "config" in f.lower()
    ]
    core_files = [
        "README.md",
        "CLAUDE.md",
        "pyproject.toml",
        "pixi.toml",
        "p3",
        ".gitignore",
        "MIGRATION_SUMMARY.md",
    ]

    other_files = [
        f for f in files if f not in coverage_files + test_files + config_files + core_files
    ]

    print(f"\nCOVERAGE FILES ({len(coverage_files)}):")
    for f in coverage_files:
        print(f"  {f}")

    print(f"\nTEST FILES ({len(test_files)}):")
    for f in test_files:
        print(f"  {f}")

    print(f"\nCONFIG FILES ({len(config_files)}):")
    for f in config_files:
        print(f"  {f}")

    print(f"\nCORE FILES ({len([f for f in core_files if f in files])}):")
    for f in core_files:
        if f in files:
            print(f"  {f}")

    print(f"\nOTHER FILES ({len(other_files)}):")
    for f in other_files:
        print(f"  {f}")

    print("=" * 80)
    print("SUMMARY:")
    print(f"  Total directories: {len(directories)}")
    print(f"  Total files: {len(files)}")
    print(f"  Coverage files to remove: {len(coverage_files)}")
    print(f"  Test files to move: {len(test_files)}")
    print(f"  Config files to organize: {len(config_files)}")
    print(f"  Files to process: {len(coverage_files) + len(test_files) + len(config_files)}")


if __name__ == "__main__":
    list_root_files()
