#!/usr/bin/env python3
"""
Setup GitHub branch protection rules to enforce M7 testing
This script configures main branch protection with mandatory M7 validation
"""

import json
import subprocess
import sys


def run_gh_command(cmd, description):
    """Run gh command with error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} - SUCCESS")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"   Error: {e.stderr}")
        return None


def setup_branch_protection():
    """Setup branch protection rules for main branch"""

    print("🛡️ Setting up GitHub branch protection rules...")

    # Branch protection configuration
    protection_config = {
        "required_status_checks": {
            "strict": True,
            "contexts": ["M7 Local Test Verification (MANDATORY)"],
        },
        "enforce_admins": False,  # Allow admins to bypass in emergencies
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 1,
        },
        "restrictions": None,  # No user/team restrictions
        "required_linear_history": False,
        "allow_force_pushes": False,
        "allow_deletions": False,
    }

    # Convert to JSON for gh command
    config_json = json.dumps(protection_config)

    # Apply branch protection
    cmd = f"""gh api repos/:owner/:repo/branches/main/protection \
        --method PUT \
        --field 'required_status_checks={config_json["required_status_checks"]}' \
        --field 'enforce_admins={config_json["enforce_admins"]}' \
        --field 'required_pull_request_reviews={config_json["required_pull_request_reviews"]}' \
        --field 'restrictions={config_json["restrictions"]}' \
        --field 'required_linear_history={config_json["required_linear_history"]}' \
        --field 'allow_force_pushes={config_json["allow_force_pushes"]}' \
        --field 'allow_deletions={config_json["allow_deletions"]}'
    """

    result = run_gh_command(cmd, "Applying branch protection rules")

    if result is not None:
        print("\n✅ Branch protection rules applied successfully!")
        print("\n📋 Protection rules summary:")
        print("   • M7 Local Test Verification: REQUIRED")
        print("   • Pull request reviews: 1 required")
        print("   • Dismiss stale reviews: YES")
        print("   • Force pushes: BLOCKED")
        print("   • Branch deletions: BLOCKED")
        print("\n🚫 PRs cannot be merged without local M7 test marker")
        return True
    else:
        print("\n❌ Failed to apply branch protection rules")
        return False


def verify_protection():
    """Verify current branch protection settings"""

    print("\n🔍 Verifying current branch protection...")

    result = run_gh_command(
        "gh api repos/:owner/:repo/branches/main/protection", "Getting current protection rules"
    )

    if result:
        try:
            protection = json.loads(result)

            print("\n📊 Current protection settings:")

            # Check required status checks
            status_checks = protection.get("required_status_checks", {})
            contexts = status_checks.get("contexts", [])

            print(f"   📋 Required status checks: {len(contexts)}")
            for context in contexts:
                print(f"     • {context}")

            # Check if M7 validation is required
            m7_required = any("M7" in context for context in contexts)
            if m7_required:
                print("   ✅ M7 validation: REQUIRED")
            else:
                print("   ❌ M7 validation: NOT REQUIRED")

            # Check PR reviews
            pr_reviews = protection.get("required_pull_request_reviews", {})
            review_count = pr_reviews.get("required_approving_review_count", 0)
            print(f"   👥 Required reviewers: {review_count}")

            return m7_required

        except json.JSONDecodeError:
            print("   ❌ Could not parse protection settings")
            return False
    else:
        print("   ❌ Could not retrieve protection settings")
        return False


def main():
    """Main function"""
    print("🛡️ GitHub Branch Protection Setup")
    print("=" * 50)

    # Check if gh CLI is available
    result = run_gh_command("gh --version", "Checking gh CLI availability")
    if not result:
        print("\n❌ GitHub CLI (gh) is required but not found")
        print("   Install: https://cli.github.com/")
        sys.exit(1)

    # Check authentication
    result = run_gh_command("gh auth status", "Checking GitHub authentication")
    if not result:
        print("\n❌ Please authenticate with GitHub CLI:")
        print("   Run: gh auth login")
        sys.exit(1)

    # Verify current settings
    current_m7_required = verify_protection()

    if current_m7_required:
        print("\n✅ M7 validation is already required - no changes needed")
    else:
        print("\n🔧 M7 validation is not required - setting up protection...")

        success = setup_branch_protection()

        if success:
            # Verify the changes
            print("\n🔍 Verifying changes...")
            if verify_protection():
                print("\n🎉 Branch protection setup completed successfully!")
                print("\n📝 Next steps:")
                print("   1. PRs now require M7 validation to pass")
                print("   2. Use 'pixi run create-pr' to create PRs with M7 testing")
                print("   3. GitHub Actions will automatically run M7 tests on PRs")
            else:
                print("\n⚠️ Changes applied but verification failed")
                sys.exit(1)
        else:
            print("\n❌ Failed to setup branch protection")
            sys.exit(1)


if __name__ == "__main__":
    main()
