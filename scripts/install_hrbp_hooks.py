#!/usr/bin/env python3
"""
Install HRBP Git Hooks

Installs post-merge hook for automatic HRBP PR tracking.
"""
import os
import stat
import subprocess
from pathlib import Path


def find_git_hooks_directory():
    """Find the git hooks directory, handling worktrees."""
    # Get git directory
    result = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Not in a git repository")

    git_dir = Path(result.stdout.strip())
    hooks_dir = git_dir / "hooks"

    return hooks_dir


def install_post_merge_hook():
    """Install post-merge hook for HRBP automation."""
    try:
        hooks_dir = find_git_hooks_directory()
        hooks_dir.mkdir(exist_ok=True)

        hook_file = hooks_dir / "post-merge"

        # Find project root to reference the Python script
        project_root = Path(__file__).parent.parent
        hrbp_hook_script = project_root / "scripts" / "post_merge_hrbp_hook.py"

        # Create the hook shell script
        hook_content = f"""#!/bin/bash
#
# Git Post-Merge Hook - HRBP Automation
# Automatically records PR merges for HRBP 20-PR cycle tracking
#

# Change to project directory
cd "{project_root}"

# Run HRBP post-merge tracking
python3 "{hrbp_hook_script}"
"""

        # Write the hook
        with open(hook_file, "w") as f:
            f.write(hook_content)

        # Make it executable
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)

        print(f"✅ HRBP post-merge hook installed: {hook_file}")
        return True

    except Exception as e:
        print(f"❌ Failed to install HRBP post-merge hook: {e}")
        return False


def check_existing_hooks():
    """Check for existing hooks that might conflict."""
    try:
        hooks_dir = find_git_hooks_directory()
        post_merge_hook = hooks_dir / "post-merge"

        if post_merge_hook.exists():
            print(f"⚠️  Existing post-merge hook found: {post_merge_hook}")
            print("📖 Content preview:")
            with open(post_merge_hook, "r") as f:
                content = f.read()
                print("   " + "\n   ".join(content.split("\n")[:10]))
                if len(content.split("\n")) > 10:
                    print("   ...")
            return True

        return False

    except Exception as e:
        print(f"❌ Error checking existing hooks: {e}")
        return False


def main():
    """Main installation logic."""
    print("🚀 Installing HRBP Git Hooks...")
    print("=" * 60)

    # Check for existing hooks
    has_existing = check_existing_hooks()

    if has_existing:
        print("\n❓ An existing post-merge hook was found.")
        response = (
            input("Do you want to replace it with HRBP automation hook? [y/N]: ").strip().lower()
        )

        if response not in ["y", "yes"]:
            print("❌ Installation cancelled")
            return False

    # Install the hook
    success = install_post_merge_hook()

    if success:
        print("\n🎉 HRBP Git Hooks Installation Complete!")
        print("=" * 60)
        print("✅ Post-merge hook installed for automatic PR tracking")
        print("📝 PRs merged to main will automatically trigger HRBP cycle checks")
        print("💡 Use 'p3 hrbp-status' to check current cycle status")
        print("🔧 Use 'p3 hrbp-manual-trigger' for emergency HRBP cycles")
    else:
        print("\n❌ HRBP Git Hooks Installation Failed!")

    return success


if __name__ == "__main__":
    main()
