#!/usr/bin/env python3
"""
HRBP Agent - Critical Deployment Script for Streamlined Policies
Addresses deployment gap: CLAUDE_STREAMLINED.md accessibility issue

This script provides the technical mechanism to make streamlined policies
actually accessible to Claude Code system through automated deployment.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


def deploy_streamlined_policies():
    """
    CRITICAL DEPLOYMENT: Make CLAUDE_STREAMLINED.md actually accessible

    Problem Solved: Claude Code system reads CLAUDE.md by default
    Solution: Create deployment mechanism with rollback capability
    """

    base_path = Path("/Users/SP14016/zitian/my_finance/.git/worktree/feature-243-check-again-2")
    current_claude = base_path / "CLAUDE.md"
    streamlined_claude = base_path / "CLAUDE_STREAMLINED.md"
    backup_claude = base_path / "CLAUDE_FULL_BACKUP.md"

    # Phase 1: Backup current full version
    if current_claude.exists():
        print(f"[DEPLOY] Backing up current CLAUDE.md to CLAUDE_FULL_BACKUP.md")
        shutil.copy2(current_claude, backup_claude)

    # Phase 2: Deploy streamlined version as primary CLAUDE.md
    if streamlined_claude.exists():
        print(f"[DEPLOY] Deploying CLAUDE_STREAMLINED.md as primary CLAUDE.md")
        shutil.copy2(streamlined_claude, current_claude)

        # Add deployment marker
        with open(current_claude, "a", encoding="utf-8") as f:
            f.write(f"\n\n<!-- STREAMLINED DEPLOYMENT: {datetime.now().isoformat()} -->")
            f.write(f"\n<!-- FULL VERSION BACKUP: CLAUDE_FULL_BACKUP.md -->")
            f.write(f"\n<!-- DEPLOYMENT SCRIPT: deploy_streamlined_policies.py -->")

        print(f"[SUCCESS] Streamlined policies now active as CLAUDE.md")
        return True
    else:
        print(f"[ERROR] CLAUDE_STREAMLINED.md not found")
        return False


def rollback_to_full_policies():
    """
    ROLLBACK MECHANISM: Restore full CLAUDE.md if streamlined causes issues
    """

    base_path = Path("/Users/SP14016/zitian/my_finance/.git/worktree/feature-243-check-again-2")
    current_claude = base_path / "CLAUDE.md"
    backup_claude = base_path / "CLAUDE_FULL_BACKUP.md"

    if backup_claude.exists():
        print(f"[ROLLBACK] Restoring full CLAUDE.md from backup")
        shutil.copy2(backup_claude, current_claude)
        print(f"[SUCCESS] Full policies restored")
        return True
    else:
        print(f"[ERROR] No backup found for rollback")
        return False


def validate_deployment():
    """
    VALIDATION: Verify deployment worked correctly
    """

    base_path = Path("/Users/SP14016/zitian/my_finance/.git/worktree/feature-243-check-again-2")
    current_claude = base_path / "CLAUDE.md"

    if current_claude.exists():
        with open(current_claude, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for streamlined markers
        is_streamlined = "STREAMLINED DEPLOYMENT" in content
        line_count = len(content.splitlines())

        print(f"[VALIDATION] CLAUDE.md exists: ✅")
        print(f"[VALIDATION] Is streamlined version: {'✅' if is_streamlined else '❌'}")
        print(f"[VALIDATION] Line count: {line_count}")
        print(
            f"[VALIDATION] Status: {'STREAMLINED ACTIVE' if is_streamlined else 'FULL VERSION ACTIVE'}"
        )

        return is_streamlined
    else:
        print(f"[VALIDATION] CLAUDE.md missing: ❌")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "deploy":
            deploy_streamlined_policies()
        elif command == "rollback":
            rollback_to_full_policies()
        elif command == "validate":
            validate_deployment()
        else:
            print("Usage: python deploy_streamlined_policies.py [deploy|rollback|validate]")
    else:
        print("HRBP Agent - Streamlined Policy Deployment Script")
        print("Usage: python deploy_streamlined_policies.py [deploy|rollback|validate]")
        print()
        print("Commands:")
        print("  deploy   - Deploy streamlined version as active CLAUDE.md")
        print("  rollback - Restore full version from backup")
        print("  validate - Check current deployment status")
