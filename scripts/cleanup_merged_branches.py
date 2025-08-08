#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup Merged Branches Script

This script automatically cleans up local and remote branches that have been merged,
optimizing the git workflow by removing unnecessary branches.
"""

import json
import logging
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Set

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BranchCleanup:
    """
    Handles cleanup of merged branches both locally and remotely.
    """

    def __init__(self, dry_run: bool = False):
        """
        Initialize branch cleanup manager.

        Args:
            dry_run: If True, only show what would be deleted without actually deleting
        """
        self.dry_run = dry_run
        self.protected_branches = {"main", "master", "develop", "staging", "production"}

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
                    merged_at = datetime.fromisoformat(
                        pr["mergedAt"].replace("Z", "+00:00")
                    )
                    if merged_at.replace(tzinfo=None) > cutoff_date:
                        recent_prs.append(pr)
                except (ValueError, KeyError):
                    continue

            return recent_prs

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get merged PRs: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PR data: {e}")
            return []

    def get_local_branches(self) -> List[str]:
        """Get list of local branches."""
        try:
            result = subprocess.run(
                ["git", "branch", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                check=True,
            )

            branches = [
                branch.strip() for branch in result.stdout.split("\n") if branch.strip()
            ]
            return [b for b in branches if b not in self.protected_branches]

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get local branches: {e}")
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
                    if branch_name not in self.protected_branches:
                        branches.append(branch_name)

            return branches

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get remote branches: {e}")
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

        Args:
            branch: Branch name to delete
            force: Use force delete (-D) instead of safe delete (-d)

        Returns:
            True if deletion was successful
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would delete local branch: {branch}")
            return True

        try:
            flag = "-D" if force else "-d"
            subprocess.run(
                ["git", "branch", flag, branch], check=True, capture_output=True
            )
            logger.info(f"✅ Deleted local branch: {branch}")
            return True

        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Failed to delete local branch {branch}: {e}")
            return False

    def delete_remote_branch(self, branch: str) -> bool:
        """
        Delete a remote branch.

        Args:
            branch: Branch name to delete

        Returns:
            True if deletion was successful
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would delete remote branch: origin/{branch}")
            return True

        try:
            subprocess.run(
                ["git", "push", "origin", "--delete", branch],
                check=True,
                capture_output=True,
            )
            logger.info(f"✅ Deleted remote branch: origin/{branch}")
            return True

        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Failed to delete remote branch {branch}: {e}")
            return False

    def cleanup_merged_branches(
        self, days_back: int = 30, force_local: bool = False
    ) -> Dict[str, int]:
        """
        Cleanup branches that have been merged.

        Args:
            days_back: Number of days to look back for merged PRs
            force_local: Use force delete for local branches

        Returns:
            Dictionary with cleanup statistics
        """
        stats = {"remote_deleted": 0, "local_deleted": 0, "skipped": 0, "errors": 0}

        logger.info("🧹 Starting branch cleanup process...")

        # Get merged PRs
        merged_prs = self.get_merged_prs(days_back)
        merged_branches = {
            pr["headRefName"] for pr in merged_prs if pr.get("headRefName")
        }

        logger.info(
            f"Found {len(merged_branches)} branches from merged PRs in last {days_back} days"
        )

        # Get current branches
        local_branches = self.get_local_branches()
        remote_branches = self.get_remote_branches()

        # Cleanup remote branches first
        logger.info("🔍 Checking remote branches for cleanup...")
        for branch in remote_branches:
            if branch in merged_branches:
                if self.delete_remote_branch(branch):
                    stats["remote_deleted"] += 1
                else:
                    stats["errors"] += 1

        # Cleanup local branches
        logger.info("🔍 Checking local branches for cleanup...")
        for branch in local_branches:
            if branch in merged_branches or self.is_branch_merged(branch):
                if self.delete_local_branch(branch, force_local):
                    stats["local_deleted"] += 1
                else:
                    stats["errors"] += 1
            else:
                logger.debug(f"Skipping branch (not merged): {branch}")
                stats["skipped"] += 1

        # Prune remote references
        logger.info("🧽 Pruning remote references...")
        try:
            if not self.dry_run:
                subprocess.run(
                    ["git", "remote", "prune", "origin"],
                    check=True,
                    capture_output=True,
                )
                logger.info("✅ Remote references pruned")
            else:
                logger.info("[DRY RUN] Would prune remote references")
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Failed to prune remote references: {e}")
            stats["errors"] += 1

        return stats

    def interactive_cleanup(self) -> None:
        """
        Run interactive branch cleanup with user confirmation.
        """
        logger.info("🔍 Analyzing branches for cleanup...")

        # Get merged PRs and branches
        merged_prs = self.get_merged_prs(30)
        merged_branches = {
            pr["headRefName"] for pr in merged_prs if pr.get("headRefName")
        }

        local_branches = self.get_local_branches()
        remote_branches = self.get_remote_branches()

        # Show what would be cleaned up
        print("\n" + "=" * 60)
        print("BRANCH CLEANUP ANALYSIS")
        print("=" * 60)

        print(f"\nMerged PRs (last 30 days): {len(merged_prs)}")
        for pr in merged_prs[:5]:  # Show first 5
            print(f"  • PR #{pr['number']}: {pr['title'][:50]}...")
        if len(merged_prs) > 5:
            print(f"  ... and {len(merged_prs) - 5} more")

        # Remote branches to delete
        remote_to_delete = [b for b in remote_branches if b in merged_branches]
        print(f"\nRemote branches to delete: {len(remote_to_delete)}")
        for branch in remote_to_delete:
            print(f"  • origin/{branch}")

        # Local branches to delete
        local_to_delete = [
            b
            for b in local_branches
            if b in merged_branches or self.is_branch_merged(b)
        ]
        print(f"\nLocal branches to delete: {len(local_to_delete)}")
        for branch in local_to_delete:
            print(f"  • {branch}")

        # Confirm deletion
        if not remote_to_delete and not local_to_delete:
            print("\n✨ No branches need cleanup!")
            return

        print(
            f"\nTotal branches to delete: {len(remote_to_delete) + len(local_to_delete)}"
        )

        confirm = input("\n❓ Proceed with cleanup? (y/N): ").strip().lower()
        if confirm != "y":
            print("Cleanup cancelled.")
            return

        # Perform cleanup
        self.dry_run = False
        stats = self.cleanup_merged_branches()

        print(f"\n✅ Cleanup completed!")
        print(f"  Remote branches deleted: {stats['remote_deleted']}")
        print(f"  Local branches deleted: {stats['local_deleted']}")
        print(f"  Errors: {stats['errors']}")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Cleanup merged git branches")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to look back for merged PRs (default: 30)",
    )
    parser.add_argument(
        "--force-local",
        action="store_true",
        help="Force delete local branches (use -D instead of -d)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode with confirmation",
    )
    parser.add_argument(
        "--auto", action="store_true", help="Run automatically without confirmation"
    )

    args = parser.parse_args()

    try:
        cleanup = BranchCleanup(dry_run=args.dry_run)

        if args.interactive:
            cleanup.interactive_cleanup()
        elif args.auto or args.dry_run:
            stats = cleanup.cleanup_merged_branches(
                days_back=args.days, force_local=args.force_local
            )

            print("\n" + "=" * 50)
            print("BRANCH CLEANUP RESULTS")
            print("=" * 50)
            print(f"Remote branches deleted: {stats['remote_deleted']}")
            print(f"Local branches deleted: {stats['local_deleted']}")
            print(f"Branches skipped: {stats['skipped']}")
            print(f"Errors encountered: {stats['errors']}")

            if args.dry_run:
                print(
                    "\n💡 This was a dry run. Use --auto to actually delete branches."
                )
        else:
            print(
                "Use --interactive for guided cleanup or --auto for automatic cleanup"
            )
            print(
                "Add --dry-run to see what would be deleted without actually deleting"
            )

    except KeyboardInterrupt:
        print("\n\n👋 Cleanup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
