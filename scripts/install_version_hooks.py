#!/usr/bin/env python3
"""
Install P3 Version Management Git Hooks

This script installs git hooks that automatically update P3 version
after git pull operations, making version tracking seamless.
"""

import os
import shutil
from pathlib import Path
import subprocess
import sys


def find_git_dir():
    """Find the git directory (handle worktrees)."""
    try:
        # Get the git directory path
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            check=True
        )
        git_dir = Path(result.stdout.strip())
        
        # If it's a relative path, make it absolute
        if not git_dir.is_absolute():
            git_dir = Path.cwd() / git_dir
            
        return git_dir
    except subprocess.CalledProcessError:
        print("❌ Error: Not in a git repository")
        return None


def install_post_merge_hook(git_dir: Path, project_root: Path) -> bool:
    """Install post-merge hook for automatic version updates."""
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    hook_source = project_root / "scripts" / "git-hooks" / "post-merge"
    hook_target = hooks_dir / "post-merge"
    
    if not hook_source.exists():
        print(f"❌ Error: Hook source not found: {hook_source}")
        return False
    
    try:
        # Check if hook already exists
        if hook_target.exists():
            # Read existing hook to see if it contains our version update logic
            with open(hook_target, 'r') as f:
                content = f.read()
            
            if "P3 version" in content and "p3_version.py" in content:
                print("ℹ️  P3 version hook already installed")
                return True
            else:
                # Backup existing hook
                backup_path = hook_target.with_suffix('.backup')
                shutil.copy2(hook_target, backup_path)
                print(f"📦 Backed up existing post-merge hook to: {backup_path}")
        
        # Install our hook
        shutil.copy2(hook_source, hook_target)
        os.chmod(hook_target, 0o755)
        
        print("✅ P3 version post-merge hook installed successfully")
        print("   This will automatically update P3 version after git pull operations")
        return True
        
    except Exception as e:
        print(f"❌ Error installing post-merge hook: {e}")
        return False


def main():
    """Main installation function."""
    print("🔧 Installing P3 Version Management Git Hooks...")
    
    # Find project root
    project_root = Path(__file__).parent.parent
    print(f"📁 Project root: {project_root}")
    
    # Find git directory
    git_dir = find_git_dir()
    if git_dir is None:
        sys.exit(1)
    
    print(f"🔗 Git directory: {git_dir}")
    
    # Install hooks
    success = True
    
    # Install post-merge hook
    if not install_post_merge_hook(git_dir, project_root):
        success = False
    
    if success:
        print("\n✅ All P3 version hooks installed successfully!")
        print("\nNext steps:")
        print("1. Run 'p3 version' to see current version")
        print("2. After git pull, version will auto-update")
        print("3. Use 'p3 version-increment [level]' for manual updates")
        print("4. Use 'p3 version-update' to manually check for git changes")
    else:
        print("\n❌ Some hooks failed to install. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()