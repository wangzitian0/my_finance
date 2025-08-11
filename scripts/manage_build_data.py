#!/usr/bin/env python3
"""
Simple build data management for multiple work trees.
Only handles essential build directory isolation per branch.
"""

import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


def get_current_branch():
    """Get current git branch."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_branch_build_dir(branch_name=None):
    """Get branch-specific build directory."""
    if branch_name is None:
        branch_name = get_current_branch()
    
    data_dir = Path("data")
    
    # For now, use existing 'build' directory for compatibility with BuildTracker
    # TODO: Implement full branch isolation later
    return data_dir / "build"


def create_build_dir():
    """Create timestamped build directory."""
    build_base = get_branch_build_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    build_dir = build_base / f"build_{timestamp}"
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Update latest symlink
    latest_link = Path("latest")
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(build_dir)
    
    print(f"Created: {build_dir}")
    return build_dir


def promote_to_release():
    """Move latest build to release directory."""
    latest = Path("latest")
    if not latest.exists():
        print("No latest build found")
        return
    
    build_dir = latest.resolve()
    release_dir = Path("data/release")
    release_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    release_name = f"release_{timestamp}_{build_dir.name}"
    release_path = release_dir / release_name
    
    print(f"Promoting {build_dir.name} to release...")
    response = input("Continue? [y/N]: ").strip().lower()
    
    if response in ['y', 'yes']:
        import shutil
        shutil.copytree(build_dir, release_path)
        print(f"Released to: {release_path}")
    else:
        print("Cancelled")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["create", "release"], 
                       help="create: new build dir, release: promote to release")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_build_dir()
    elif args.command == "release":
        promote_to_release()


if __name__ == "__main__":
    main()