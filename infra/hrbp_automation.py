#!/usr/bin/env python3
"""
HRBP Automation Command Interface

Provides command-line interface for HRBP automation system.
Integrates with p3 workflow for 20-PR cycle automation.

NOTE: This is the legacy CLI interface. For comprehensive HRBP functionality,
use the new comprehensive CLI: infra/hrbp_comprehensive_cli.py
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    """Main CLI interface for HRBP automation."""
    parser = argparse.ArgumentParser(
        description="HRBP Automation - 20-PR Cycle Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python infra/hrbp_automation.py status
  python infra/hrbp_automation.py record-pr 123
  python infra/hrbp_automation.py manual-trigger
  python infra/hrbp_automation.py history --limit 5
        """,
    )

    parser.add_argument(
        "command",
        choices=["status", "record-pr", "manual-trigger", "history", "config"],
        help="HRBP automation command",
    )

    parser.add_argument(
        "pr_number", nargs="?", type=int, help="PR number (required for record-pr command)"
    )

    parser.add_argument(
        "--limit", type=int, default=10, help="Limit for history command (default: 10)"
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without executing"
    )

    args = parser.parse_args()

    try:
        # Add project root to Python path for imports
        import sys

        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        # Import HRBP tracker
        from common.hrbp_pr_tracker import get_hrbp_tracker

        tracker = get_hrbp_tracker()

        if args.command == "status":
            status = tracker.get_cycle_status()
            print_status(status)

        elif args.command == "record-pr":
            if not args.pr_number:
                print("❌ Error: PR number is required for record-pr command")
                sys.exit(1)

            if args.dry_run:
                print(f"🔍 DRY RUN: Would record PR #{args.pr_number}")
                return

            triggered = tracker.record_pr_merge(args.pr_number)
            if triggered:
                print(f"✅ PR #{args.pr_number} recorded and HRBP cycle triggered!")
            else:
                print(f"✅ PR #{args.pr_number} recorded")

        elif args.command == "manual-trigger":
            if args.dry_run:
                print("🔍 DRY RUN: Would manually trigger HRBP cycle")
                return

            print("⚠️  Manual HRBP trigger requested")
            confirmation = (
                input("Are you sure you want to manually trigger HRBP cycle? [y/N]: ")
                .strip()
                .lower()
            )

            if confirmation in ["y", "yes"]:
                success = tracker.manual_trigger_hrbp_cycle()
                if success:
                    print("✅ Manual HRBP cycle triggered successfully")
                else:
                    print("❌ Manual HRBP cycle trigger failed")
                    sys.exit(1)
            else:
                print("❌ Manual trigger cancelled")

        elif args.command == "history":
            history = tracker.get_trigger_history(args.limit)
            print_history(history)

        elif args.command == "config":
            config = tracker.config
            print(json.dumps(config, indent=2))

    except ImportError as e:
        print(f"❌ Failed to import HRBP tracker: {e}")
        print("Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ HRBP automation error: {e}")
        sys.exit(1)


def print_status(status):
    """Print formatted HRBP cycle status."""
    print("\n" + "=" * 60)
    print("🤖 HRBP AUTOMATION STATUS")
    print("=" * 60)

    print(f"📊 Status: {'🟢 Enabled' if status['enabled'] else '🔴 Disabled'}")
    print(f"🎯 PR Threshold: {status['pr_threshold']} PRs per cycle")
    print(f"📈 Total PRs Tracked: {status['total_prs_tracked']}")
    print(f"🔄 Current Cycle PRs: {status['current_cycle_prs']}")
    print(f"⏳ PRs Until Next Trigger: {status['prs_until_next_trigger']}")
    print(f"📝 Last PR Number: {status['last_pr_number']}")
    print(f"🚀 Total HRBP Triggers: {status['total_triggers']}")

    if status["last_trigger"]:
        trigger = status["last_trigger"]
        print(f"\n📋 Last HRBP Trigger:")
        print(f"   ID: {trigger['trigger_id']}")
        print(f"   Status: {trigger['status']}")
        print(f"   PR Range: {trigger['starting_pr']}-{trigger['ending_pr']}")
        print(f"   Workflows: {', '.join(trigger['workflows_triggered'])}")
        print(f"   Timestamp: {trigger['timestamp']}")
    else:
        print(f"\n📋 No HRBP triggers executed yet")

    # Progress bar for current cycle
    current = status["current_cycle_prs"]
    threshold = status["pr_threshold"]
    progress = current / threshold
    bar_length = 30
    filled = int(bar_length * progress)
    bar = "█" * filled + "░" * (bar_length - filled)

    print(f"\n🔄 Current Cycle Progress:")
    print(f"   [{bar}] {current}/{threshold} PRs ({progress:.1%})")


def print_history(history):
    """Print formatted HRBP trigger history."""
    print("\n" + "=" * 60)
    print("📜 HRBP TRIGGER HISTORY")
    print("=" * 60)

    if not history:
        print("No HRBP triggers found")
        return

    for i, trigger in enumerate(reversed(history), 1):
        status_icon = {"completed": "✅", "failed": "❌", "running": "🔄", "pending": "⏳"}.get(
            trigger["status"], "❓"
        )

        print(f"\n{i}. {status_icon} {trigger['trigger_id']}")
        print(f"   Status: {trigger['status']}")
        print(
            f"   PR Range: {trigger['starting_pr']}-{trigger['ending_pr']} ({trigger['pr_count']} PRs)"
        )
        print(f"   Timestamp: {trigger['timestamp']}")
        print(f"   Workflows: {', '.join(trigger['workflows_triggered'])}")

        if trigger.get("completion_timestamp"):
            print(f"   Completed: {trigger['completion_timestamp']}")

        if trigger.get("error_message"):
            print(f"   Error: {trigger['error_message']}")


if __name__ == "__main__":
    print("💡 TIP: For comprehensive HRBP functionality, try the new CLI:")
    print("   python infra/hrbp_comprehensive_cli.py --help")
    print()
    main()
