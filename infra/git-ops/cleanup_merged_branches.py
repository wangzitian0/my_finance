#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup Merged Branches Script

This script automatically cleans up local and remote branches that have been merged,
optimizing the git workflow by removing unnecessary branches.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Set


class BranchCleanup:
    """
    Handles cleanup of merged branches both locally and remotely.
    """

    def __init__(self):
        """
        Initialize branch cleanup manager.
        """
        self.protected_branches = {"main", "master", "develop", "staging", "production"}
        self.current_branch = self.get_current_branch()
        self.active_worktree_branches = self.get_active_worktree_branches()

    def get_merged_prs(self, days_back: int = 30) -> List[Dict]:
        """
        Get list of recently merged PRs.

        Args:
            days_back: Number of days to look back for merged PRs

        Returns:
            List of merged PR information
        """
        try:
            # Get merged PRs from GitHub CLI
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "list",
                    "--state",
                    "merged",
                    "--limit",
                    "50",
                    "--json",
                    "number,title,headRefName,mergedAt",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            prs = json.loads(result.stdout)

            # Filter PRs merged within the specified timeframe
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_prs = []

            for pr in prs:
                try:
                    merged_at = datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
                    if merged_at.replace(tzinfo=None) > cutoff_date:
                        recent_prs.append(pr)
                except (ValueError, KeyError):
                    continue

            return recent_prs

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []

    def get_current_branch(self) -> str:
        """Get the current branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""

    def get_active_worktree_branches(self) -> Set[str]:
        """Get branches that are actively checked out in worktrees."""
        try:
            result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )

            active_branches = set()
            for line in result.stdout.split("\n"):
                if line.startswith("branch "):
                    branch = line.split("branch ")[1].strip()
                    if branch.startswith("refs/heads/"):
                        branch = branch.replace("refs/heads/", "")
                    active_branches.add(branch)

            return active_branches

        except subprocess.CalledProcessError:
            return set()

    def is_branch_protected(self, branch: str) -> bool:
        """
        Check if a branch should be protected from deletion.

        Args:
            branch: Branch name to check

        Returns:
            True if branch should be protected
        """
        return (
            branch in self.protected_branches
            or branch == self.current_branch
            or branch in self.active_worktree_branches
        )

    def get_local_branches(self) -> List[str]:
        """Get list of local branches."""
        try:
            result = subprocess.run(
                ["git", "branch", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                check=True,
            )

            branches = [branch.strip() for branch in result.stdout.split("\n") if branch.strip()]
            return [b for b in branches if not self.is_branch_protected(b)]

        except subprocess.CalledProcessError:
            return []

    def get_remote_branches(self) -> List[str]:
        """Get list of remote branches."""
        try:
            result = subprocess.run(
                ["git", "branch", "-r", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                check=True,
            )

            branches = []
            for branch in result.stdout.split("\n"):
                branch = branch.strip()
                if branch and branch.startswith("origin/") and branch != "origin/HEAD":
                    branch_name = branch.replace("origin/", "")
                    if not self.is_branch_protected(branch_name):
                        branches.append(branch_name)

            return branches

        except subprocess.CalledProcessError:
            return []

    def is_branch_merged(self, branch: str, target_branch: str = "main") -> bool:
        """
        Check if a branch has been merged into target branch.

        Args:
            branch: Branch name to check
            target_branch: Target branch (usually main/master)

        Returns:
            True if branch is merged
        """
        try:
            # Check if branch exists in merge-base
            result = subprocess.run(
                [
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    branch,
                    f"origin/{target_branch}",
                ],
                capture_output=True,
                text=True,
            )

            return result.returncode == 0

        except subprocess.CalledProcessError:
            return False

    def delete_local_branch(self, branch: str, force: bool = False) -> bool:
        """
        Delete a local branch.
        """
        try:
            flag = "-D" if force else "-d"
            subprocess.run(["git", "branch", flag, branch], check=True, capture_output=True)
            print(f"✅ Deleted local: {branch}")
            return True
        except subprocess.CalledProcessError:
            return False

    def delete_remote_branch(self, branch: str) -> bool:
        """
        Delete a remote branch.
        """
        try:
            subprocess.run(
                ["git", "push", "origin", "--delete", branch], check=True, capture_output=True
            )
            print(f"✅ Deleted remote: origin/{branch}")
            return True
        except subprocess.CalledProcessError:
            return False

    def get_inactive_branches(self, days_back: int = 14) -> Set[str]:
        """
        Get branches that haven't been active for specified days and have no open PRs.
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        inactive_branches = set()

        try:
            # Get all local branches with last commit date
            result = subprocess.run(
                [
                    "git",
                    "for-each-ref",
                    "--format=%(refname:short) %(committerdate:iso8601)",
                    "refs/heads/",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.rsplit(" ", 1)
                if len(parts) != 2:
                    continue

                branch, date_str = parts
                if self.is_branch_protected(branch):
                    continue

                try:
                    commit_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    if commit_date.replace(tzinfo=None) < cutoff_date:
                        # Check if branch has open PR
                        pr_result = subprocess.run(
                            [
                                "gh",
                                "pr",
                                "list",
                                "--head",
                                branch,
                                "--state",
                                "open",
                                "--json",
                                "number",
                            ],
                            capture_output=True,
                            text=True,
                        )

                        if pr_result.returncode == 0:
                            prs = json.loads(pr_result.stdout)
                            if not prs:  # No open PRs
                                inactive_branches.add(branch)
                except ValueError:
                    continue

        except subprocess.CalledProcessError:
            pass

        return inactive_branches

    def cleanup_branches(self, days_back: int = 14) -> None:
        """
        Simple cleanup: delete merged branches and inactive branches.

        Args:
            days_back: Number of days to look back for inactive branches
        """
        print("🧹 Starting branch cleanup...")

        deleted_count = 0

        # 1. Get merged branches
        merged_prs = self.get_merged_prs(30)
        merged_branches = {pr["headRefName"] for pr in merged_prs if pr.get("headRefName")}

        # 2. Get inactive branches (configurable days, no PR)
        inactive_branches = self.get_inactive_branches(days_back)

        branches_to_delete = merged_branches | inactive_branches

        print(f"📊 Found {len(merged_branches)} merged branches")
        print(f"📊 Found {len(inactive_branches)} inactive branches ({days_back}+ days, no PR)")
        print(f"📊 Total to delete: {len(branches_to_delete)}")

        if not branches_to_delete:
            print("✨ No branches need cleanup!")
            return

        # 3. Delete remote branches
        remote_branches = self.get_remote_branches()
        for branch in remote_branches:
            if branch in branches_to_delete:
                if self.delete_remote_branch(branch):
                    deleted_count += 1

        # 4. Delete local branches
        local_branches = self.get_local_branches()
        for branch in local_branches:
            if branch in branches_to_delete or self.is_branch_merged(branch):
                if self.delete_local_branch(branch, force=True):
                    deleted_count += 1

        # 5. Prune remote references
        try:
            subprocess.run(["git", "remote", "prune", "origin"], check=True, capture_output=True)
            print("✅ Remote references pruned")
        except subprocess.CalledProcessError:
            pass

        print(f"✅ Cleanup completed! Deleted {deleted_count} branches")


def main():
    """Main function - simple branch cleanup."""
    import argparse

    parser = argparse.ArgumentParser(description="Cleanup merged and inactive git branches")
    parser.add_argument("--auto", action="store_true", help="Run automatically without prompts")
    parser.add_argument(
        "--days", type=int, default=14, help="Days to look back for inactive branches"
    )
    args = parser.parse_args()

    try:
        cleanup = BranchCleanup()
        cleanup.cleanup_branches(args.days)
    except KeyboardInterrupt:
        print("\n\n👋 Cleanup cancelled.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
