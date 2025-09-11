#!/usr/bin/env python3
"""
Worktree Python Environment Isolation Manager
Repo-internal worktree isolation solution using pixi/Python management

Core Features:
1. Auto-detect worktree environment and activate isolated Python
2. Global infrastructure (ansible/docker) reuse
3. Zero-configuration, one-click workflow
4. Completely managed within git repo
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


class WorktreeIsolationManager:
    """Worktree Isolation Environment Manager"""

    def __init__(self):
        self.repo_root = self._get_repo_root()
        self.worktree_root = Path.cwd()
        self.worktree_name = self.worktree_root.name
        self.is_worktree = self._is_worktree()

    def _get_repo_root(self) -> Path:
        """Get git repository root directory"""
        try:
            # Check if this is a worktree
            result = subprocess.run(
                ["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True, check=True
            )
            git_common_dir = Path(result.stdout.strip())

            # If git-common-dir contains worktree path, this is a worktree
            if "worktree" in str(git_common_dir):
                # Main repository is parent directory of .git
                return git_common_dir.parent
            else:
                # This is the main repository
                result = subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return Path(result.stdout.strip())
        except subprocess.CalledProcessError:
            return Path.cwd()

    def _is_worktree(self) -> bool:
        """Detect if currently in a worktree"""
        try:
            # Use git-dir to detect, worktree git-dir contains worktrees path
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"], capture_output=True, text=True, check=True
            )
            git_dir = result.stdout.strip()
            # If git-dir contains worktrees path, this is a worktree
            return "worktrees" in git_dir
        except subprocess.CalledProcessError:
            return False

    def _get_expected_python(self) -> Path:
        """Get expected worktree Python path"""
        return self.worktree_root / ".pixi/envs/default/bin/python"

    def _is_python_isolated(self) -> bool:
        """Check if current Python is isolated"""
        expected_python = self._get_expected_python()
        if not expected_python.exists():
            return False

        try:
            current_python = Path(sys.executable).resolve()
            expected_python_resolved = expected_python.resolve()
            return current_python == expected_python_resolved
        except Exception:
            return False

    def _ensure_pixi_env(self) -> bool:
        """Ensure pixi environment exists"""
        expected_python = self._get_expected_python()
        if not expected_python.exists():
            print("🔧 Installing pixi environment...")
            try:
                subprocess.run(["pixi", "install"], cwd=self.worktree_root, check=True)
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install pixi environment")
                return False
        return True

    def auto_switch_python(self) -> bool:
        """Automatically switch to worktree-isolated Python environment"""
        if not self.is_worktree:
            return True  # Main repository doesn't need switching

        if self._is_python_isolated():
            return True  # Already isolated

        # Ensure pixi environment exists
        if not self._ensure_pixi_env():
            return False

        expected_python = self._get_expected_python()
        if not expected_python.exists():
            print(f"❌ Python environment not found: {expected_python}")
            return False

        # Re-execute script using correct Python
        print(f"🔄 Auto-switching to worktree Python environment...")
        print(f"   Worktree: {self.worktree_name}")
        print(f"   Python: {expected_python}")

        try:
            # Re-execute current script
            os.execv(str(expected_python), [str(expected_python)] + sys.argv)
        except Exception as e:
            print(f"❌ Failed to switch Python: {e}")
            return False

    def get_status(self) -> Dict:
        """Get worktree environment status"""
        return {
            "repo_root": str(self.repo_root),
            "worktree_root": str(self.worktree_root),
            "worktree_name": self.worktree_name,
            "is_worktree": self.is_worktree,
            "python_executable": sys.executable,
            "python_version": sys.version.split()[0],
            "python_isolated": self._is_python_isolated(),
            "pixi_env_exists": self._get_expected_python().exists(),
            "expected_python": str(self._get_expected_python()),
        }

    def print_status(self):
        """Print worktree environment status"""
        status = self.get_status()

        print("🔍 Worktree Environment Status")
        print("=" * 40)
        print(f"Repository: {Path(status['repo_root']).name}")
        print(f"Worktree: {status['worktree_name']}")
        print(f"Is Worktree: {status['is_worktree']}")
        print(f"Python: {status['python_version']} at {status['python_executable']}")

        if status["is_worktree"]:
            if status["python_isolated"]:
                print("✅ Python environment isolated")
            else:
                print("❌ Python environment not isolated")
                print(f"   Expected: {status['expected_python']}")
        else:
            print("ℹ️  Main repository (no isolation needed)")

    def verify_packages(self):
        """Verify key Python package availability"""
        print("\n🔍 Package Availability Check")
        print("-" * 30)

        packages = ["pandas", "numpy", "requests", "neo4j", "yfinance"]
        available = []
        missing = []

        for pkg in packages:
            try:
                __import__(pkg)
                available.append(pkg)
            except ImportError:
                missing.append(pkg)

        if available:
            print(f"✅ Available: {', '.join(available)}")
        if missing:
            print(f"⚠️  Missing: {', '.join(missing)}")
        else:
            print("🎉 All core packages available!")

    def init_worktree(self):
        """Initialize worktree environment (if needed)"""
        print(f"🏗️  Initializing worktree: {self.worktree_name}")

        if not self.is_worktree:
            print("ℹ️  This is the main repository, no worktree initialization needed")
            return

        # Ensure pixi environment exists
        self._ensure_pixi_env()

        # Check if Python switching is needed
        if not self._is_python_isolated():
            print("💡 Run this script again to activate Python isolation")
            return

        print("✅ Worktree environment initialized successfully")

    def setup_global_infrastructure(self):
        """Setup global infrastructure reuse (ansible/docker etc.)"""
        print("🌐 Setting up global infrastructure reuse...")

        # Configure paths and settings for global tools like ansible/docker
        # Since these tools are relatively stable, they can be reused via pixi in each worktree

        global_config = {
            "ansible_playbooks": str(self.repo_root / "infra/ansible"),
            "docker_configs": str(self.repo_root / "infra/docker"),
            "shared_scripts": str(self.repo_root / "scripts"),
        }

        config_file = self.worktree_root / ".worktree_config.json"
        with open(config_file, "w") as f:
            json.dump(global_config, f, indent=2)

        print(f"✅ Global infrastructure config saved: {config_file}")


def main():
    """Main entry function"""
    manager = WorktreeIsolationManager()

    if len(sys.argv) < 2:
        print("Usage: python worktree_isolation.py <command>")
        print("Commands:")
        print("  init      - Initialize worktree environment")
        print("  status    - Show environment status")
        print("  verify    - Verify environment and packages")
        print("  setup-global - Setup global infrastructure reuse")
        return

    command = sys.argv[1]

    if command == "init":
        manager.init_worktree()
    elif command == "status":
        manager.print_status()
    elif command == "verify":
        manager.print_status()
        manager.verify_packages()
    elif command == "setup-global":
        manager.setup_global_infrastructure()
    elif command == "auto-switch":
        # Internal command: automatically switch Python environment
        return manager.auto_switch_python()
    else:
        print(f"Unknown command: {command}")
        return


if __name__ == "__main__":
    main()
