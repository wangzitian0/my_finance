#!/usr/bin/env python3
"""
Simple P3 Version Management - Under 100 lines
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

VERSION_FILE = Path(__file__).parent / ".p3_version.json"


def get_git_info():
    """Get current git hash and branch."""
    try:
        hash_cmd = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        branch_cmd = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )
        return (
            hash_cmd.stdout.strip()[:8] if hash_cmd.returncode == 0 else "unknown",
            branch_cmd.stdout.strip() if branch_cmd.returncode == 0 else "unknown",
        )
    except:
        return "unknown", "unknown"


def load_version():
    """Load version from file or create default."""
    if VERSION_FILE.exists():
        with open(VERSION_FILE, "r") as f:
            return json.load(f)
    return {"major": 1, "minor": 0, "patch": 0, "git_hash": "", "git_branch": ""}


def save_version(data):
    """Save version to file."""
    data["last_updated"] = datetime.now().isoformat()
    with open(VERSION_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_version_string():
    """Get formatted version string."""
    data = load_version()
    git_hash, git_branch = get_git_info()

    # Auto-increment patch if git changed
    if git_hash != data.get("git_hash") and git_hash != "unknown":
        data["patch"] += 1
        data["git_hash"] = git_hash
        data["git_branch"] = git_branch
        save_version(data)

    version = f"{data['major']}.{data['minor']}.{data['patch']}"
    if git_branch != "main":
        version += f"-{git_branch}"
    if git_hash != "unknown":
        version += f"+{git_hash}"
    return version


def increment_version(level="patch"):
    """Manually increment version."""
    data = load_version()
    git_hash, git_branch = get_git_info()

    if level == "major":
        data["major"] += 1
        data["minor"] = 0
        data["patch"] = 0
    elif level == "minor":
        data["minor"] += 1
        data["patch"] = 0
    else:  # patch
        data["patch"] += 1

    data["git_hash"] = git_hash
    data["git_branch"] = git_branch
    save_version(data)
    return get_version_string()


def main():
    """CLI interface."""
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "increment":
            level = sys.argv[2] if len(sys.argv) > 2 else "patch"
            print(f"Version: {increment_version(level)}")
        elif cmd == "info":
            print(f"P3 Version: {get_version_string()}")
        else:
            print(f"Usage: {sys.argv[0]} [info|increment [major|minor|patch]]")
    else:
        print(f"P3 Version: {get_version_string()}")


if __name__ == "__main__":
    main()
