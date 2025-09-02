#!/usr/bin/env python3
"""
P3 Tool Version Management

Provides version tracking for the P3 CLI tool to facilitate bug tracking
and compatibility management. Version is automatically updated based on 
git commits and can be manually incremented.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class P3VersionManager:
    """Manages P3 tool versioning with automatic git-based updates."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent
        self.version_file = self.project_root / ".p3_version.json"
        self._version_data = None
    
    def _load_version_data(self) -> Dict:
        """Load version data from file or create default."""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Default version data
        return {
            "major": 1,
            "minor": 0,
            "patch": 0,
            "build": 0,
            "git_hash": self._get_git_hash(),
            "git_branch": self._get_git_branch(),
            "last_updated": datetime.now().isoformat(),
            "update_count": 0
        }
    
    def _save_version_data(self, data: Dict) -> None:
        """Save version data to file."""
        with open(self.version_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _get_git_hash(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                return result.stdout.strip()[:8]  # Short hash
        except Exception:
            pass
        return "unknown"
    
    def _get_git_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"
    
    def _get_commits_since_last_update(self) -> int:
        """Get number of commits since last version update."""
        try:
            data = self._load_version_data()
            if "git_hash" in data and data["git_hash"] != "unknown":
                result = subprocess.run(
                    ["git", "rev-list", "--count", f"{data['git_hash']}..HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                if result.returncode == 0:
                    return int(result.stdout.strip())
        except Exception:
            pass
        return 0
    
    def get_version_info(self) -> Dict:
        """Get complete version information."""
        if self._version_data is None:
            self._version_data = self._load_version_data()
        
        # Check if git state has changed
        current_hash = self._get_git_hash()
        current_branch = self._get_git_branch()
        
        if (current_hash != self._version_data.get("git_hash") or 
            current_branch != self._version_data.get("git_branch")):
            # Auto-increment build number on git changes
            self._version_data["build"] += 1
            self._version_data["git_hash"] = current_hash
            self._version_data["git_branch"] = current_branch
            self._version_data["last_updated"] = datetime.now().isoformat()
            self._version_data["update_count"] += 1
            self._save_version_data(self._version_data)
        
        # Add runtime information
        commits_ahead = self._get_commits_since_last_update()
        
        return {
            **self._version_data,
            "version_string": self.get_version_string(),
            "commits_ahead": commits_ahead,
            "is_dirty": self._is_git_dirty()
        }
    
    def get_version_string(self) -> str:
        """Get formatted version string."""
        data = self._load_version_data()
        base_version = f"{data['major']}.{data['minor']}.{data['patch']}"
        
        if data.get("build", 0) > 0:
            base_version += f".{data['build']}"
        
        # Add git info for development builds
        git_hash = data.get("git_hash", "unknown")
        git_branch = data.get("git_branch", "unknown")
        
        if git_branch and git_branch != "main" and git_branch != "unknown":
            base_version += f"-{git_branch}"
        
        if git_hash != "unknown":
            base_version += f"+{git_hash}"
        
        return base_version
    
    def _is_git_dirty(self) -> bool:
        """Check if working directory has uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            return False
    
    def _get_git_dir(self) -> Optional[Path]:
        """Get git directory path (handles worktrees)."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                git_dir = Path(result.stdout.strip())
                if not git_dir.is_absolute():
                    git_dir = self.project_root / git_dir
                return git_dir
        except Exception:
            pass
        return None
    
    def increment_version(self, level: str = "patch") -> str:
        """Manually increment version."""
        data = self._load_version_data()
        
        if level == "major":
            data["major"] += 1
            data["minor"] = 0
            data["patch"] = 0
            data["build"] = 0
        elif level == "minor":
            data["minor"] += 1
            data["patch"] = 0
            data["build"] = 0
        elif level == "patch":
            data["patch"] += 1
            data["build"] = 0
        elif level == "build":
            data["build"] += 1
        
        data["git_hash"] = self._get_git_hash()
        data["git_branch"] = self._get_git_branch()
        data["last_updated"] = datetime.now().isoformat()
        data["update_count"] += 1
        
        self._save_version_data(data)
        self._version_data = None  # Reset cache
        
        return self.get_version_string()
    
    def update_on_pull(self) -> bool:
        """Update version after git pull. Returns True if version was updated."""
        old_hash = self._load_version_data().get("git_hash")
        new_hash = self._get_git_hash()
        
        if old_hash != new_hash:
            # Auto-increment build on git pull
            self.increment_version("build")
            return True
        
        return False
    
    def check_for_updates(self) -> Dict:
        """Check if version needs updating based on git changes."""
        info = self.get_version_info()
        current_hash = self._get_git_hash()
        current_branch = self._get_git_branch()
        
        needs_update = False
        reasons = []
        
        if current_hash != info.get("git_hash"):
            needs_update = True
            reasons.append("Git hash changed")
        
        if current_branch != info.get("git_branch"):
            needs_update = True
            reasons.append("Git branch changed")
        
        if info.get("commits_ahead", 0) > 0:
            needs_update = True
            reasons.append(f"{info['commits_ahead']} commits ahead")
        
        if info.get("is_dirty"):
            reasons.append("Working directory has uncommitted changes")
        
        return {
            "needs_update": needs_update,
            "reasons": reasons,
            "current_version": info["version_string"],
            "git_hash": current_hash,
            "git_branch": current_branch,
        }
    
    def get_version_history(self) -> List[Dict]:
        """Get version history from git log."""
        try:
            # Get git log for the last 10 commits related to version changes
            result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--grep=version", "--grep=Version", 
                 "--grep=increment", "--grep=update"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            history = []
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(' ', 1)
                        if len(parts) == 2:
                            commit_hash, message = parts
                            history.append({
                                "hash": commit_hash,
                                "message": message
                            })
            
            # Add current version info
            current_info = self.get_version_info()
            history.insert(0, {
                "hash": current_info["git_hash"],
                "message": f"Current version: {current_info['version_string']}",
                "current": True
            })
            
            return history
        except Exception:
            return []


def get_version_manager() -> P3VersionManager:
    """Get the global version manager instance."""
    return P3VersionManager()


def get_p3_version() -> str:
    """Get current P3 version string."""
    return get_version_manager().get_version_string()


def print_version_info():
    """Print comprehensive version information."""
    manager = get_version_manager()
    info = manager.get_version_info()
    
    print(f"🔧 P3 Tool Version: {info['version_string']}")
    print(f"🌿 Git Branch: {info['git_branch']}")
    print(f"📋 Git Hash: {info['git_hash']}")
    print(f"🕐 Last Updated: {info['last_updated'][:19].replace('T', ' ')}")
    print(f"🔄 Update Count: {info['update_count']}")
    
    if info.get("is_dirty"):
        print("⚠️  Working directory has uncommitted changes")
    
    if info.get("commits_ahead", 0) > 0:
        print(f"📈 {info['commits_ahead']} commits ahead of last version update")
    
    # Add hook installation status
    git_dir = manager._get_git_dir()
    if git_dir:
        post_merge_hook = git_dir / "hooks" / "post-merge"
        if post_merge_hook.exists():
            print("✅ Git hooks installed (automatic version updates enabled)")
        else:
            print("⚠️  Git hooks not installed - run 'p3 install-version-hooks' for automatic updates")


def print_update_check():
    """Print version update check information."""
    manager = get_version_manager()
    check_info = manager.check_for_updates()
    
    print(f"🔍 Version Update Check")
    print(f"Current Version: {check_info['current_version']}")
    print(f"Git Branch: {check_info['git_branch']}")
    print(f"Git Hash: {check_info['git_hash']}")
    
    if check_info["needs_update"]:
        print("\n⚠️  Version update recommended:")
        for reason in check_info["reasons"]:
            print(f"   • {reason}")
        print("\n💡 Run 'p3 version-update' to update version automatically")
    else:
        print("\n✅ Version is up to date")
        
    if check_info["reasons"] and not check_info["needs_update"]:
        print("\n📝 Notes:")
        for reason in check_info["reasons"]:
            print(f"   • {reason}")


def print_version_history():
    """Print version history from git."""
    manager = get_version_manager()
    history = manager.get_version_history()
    
    print("📚 P3 Version History")
    print("=" * 50)
    
    if not history:
        print("No version history available")
        return
    
    for entry in history:
        if entry.get("current"):
            print(f"📍 {entry['hash']} - {entry['message']}")
        else:
            print(f"   {entry['hash']} - {entry['message']}")
    
    if len(history) > 1:
        print(f"\n💡 Showing last {len(history)-1} version-related commits")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        manager = get_version_manager()
        
        if command == "increment":
            level = sys.argv[2] if len(sys.argv) > 2 else "patch"
            new_version = manager.increment_version(level)
            print(f"Version incremented to: {new_version}")
        elif command == "update-on-pull":
            if manager.update_on_pull():
                print(f"Version updated to: {manager.get_version_string()}")
            else:
                print("No version update needed")
        elif command == "info":
            print_version_info()
        elif command == "check-updates":
            print_update_check()
        elif command == "history":
            print_version_history()
        else:
            print("Usage: python p3_version.py [increment|update-on-pull|info|check-updates|history] [major|minor|patch|build]")
    else:
        print_version_info()