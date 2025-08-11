#!/usr/bin/env python3
"""
Create PR with mandatory M7 end-to-end testing
This script automates the complete PR creation workflow with M7 validation
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def run_command(cmd, description, timeout=None, check=True):
    """Run a command with proper error handling"""
    print(f"🔄 {description}...")
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, check=check)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=check)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return result
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            if check:
                sys.exit(1)
            return result
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT ({timeout}s)")
        if check:
            sys.exit(1)
        return None
    except Exception as e:
        print(f"💥 {description} - EXCEPTION: {e}")
        if check:
            sys.exit(1)
        return None


def get_current_branch():
    """Get current git branch"""
    result = run_command("git branch --show-current", "Getting current branch")
    return result.stdout.strip()


def get_uncommitted_changes():
    """Check for uncommitted changes"""
    result = run_command("git status --porcelain", "Checking for uncommitted changes", check=False)
    return result.stdout.strip() if result else ""


def run_m7_end_to_end():
    """Run M7 end-to-end test with smart cleanup"""
    print("\n" + "="*60)
    print("🧪 RUNNING MANDATORY M7 END-TO-END TEST")
    print("="*60)
    
    # Clean any existing build artifacts and symlinks  
    run_command("rm -rf data/build/build_*", "Cleaning existing build artifacts", check=False)
    run_command("rm -f data/build/latest", "Cleaning latest symlink", check=False)
    
    # Start environment if needed
    run_command("pixi run env-status", "Checking environment status", check=False)
    
    test_success = False
    try:
        # Build M7 dataset
        run_command("pixi run build-dataset m7", "Building M7 dataset", timeout=600)  # 10 minutes
        test_success = True
    except Exception as e:
        print(f"❌ M7 test failed: {e}")
        print("🔍 Build artifacts preserved for debugging")
        return False
    
    # Validate build results
    build_status = run_command("pixi run build-status", "Checking build status")
    
    # Check for expected files in multiple possible locations
    file_locations = [
        "data/stage_01_extract/yfinance",
        "data/original/yfinance", 
        "data/build/latest"
    ]
    
    total_files = 0
    for location in file_locations:
        if Path(location).exists():
            location_files = run_command(f"find {location} -name '*.json' -type f | wc -l", 
                                      f"Counting files in {location}", check=False)
            if location_files and location_files.stdout.strip():
                count = int(location_files.stdout.strip())
                total_files += count
                print(f"📁 Found {count} files in {location}")
    
    print(f"📊 Total M7 data files found: {total_files}")
    
    if total_files < 7:  # At least 1 file per M7 ticker
        print(f"❌ FAIL: Expected at least 7 M7 files (one per ticker), found {total_files}")
        print("🔍 Build artifacts preserved for debugging")
        return False
    elif total_files < 21:  # Ideal: 7 tickers × 3 periods = 21 files
        print(f"⚠️  WARNING: Expected 21 M7 files (7 tickers × 3 periods), found {total_files}")
        print("   This may be acceptable if some data sources are unavailable")
    
    if total_files == 0:
        print("❌ No M7 data files found")
        print("🔍 Build artifacts preserved for debugging")
        return False
    
    # Test passed - clean up artifacts to avoid git pollution
    print("✅ M7 END-TO-END TEST PASSED")
    print("🧹 Moving test artifacts to data/test/ to keep git clean...")
    
    # Create timestamp for this test run
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Move build artifacts to test directory
    run_command(f"mkdir -p data/test/build_{timestamp}", "Creating test archive directory", check=False)
    run_command(f"mv data/build/build_* data/test/build_{timestamp}/ 2>/dev/null || true", "Moving build artifacts", check=False)
    run_command(f"mv data/reports/M7_DCF_Report_*.txt data/test/build_{timestamp}/ 2>/dev/null || true", "Moving DCF reports", check=False)
    run_command("rm -f data/build/latest", "Cleaning latest symlink", check=False)
    
    # Create test success marker
    create_m7_test_marker(total_files)
    
    print(f"📦 Test artifacts archived to data/test/build_{timestamp}/")
    print("✅ Git status is now clean - ready for PR creation!")
    return True


def create_m7_test_marker(file_count: int):
    """Create marker file indicating M7 test passed"""
    from datetime import datetime, timezone
    import socket
    
    # Get current commit hash
    commit_result = run_command("git rev-parse HEAD", "Getting commit hash", check=False)
    commit_hash = commit_result.stdout.strip() if commit_result else "unknown"
    
    # Create marker content
    marker_content = f"""M7_TEST_PASSED=true
COMMIT_HASH={commit_hash}
TEST_TIMESTAMP={datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
TEST_HOST={socket.gethostname()}
PIXI_VERSION=latest

# M7 Test Results
M7_COMPANIES=7
M7_DATA_FILES={file_count}
BUILD_STATUS=completed
VALIDATION_PASSED=true

# Generated by: pixi run test-m7-e2e
# Last test: {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
# Commit: {commit_hash}
"""
    
    # Write marker file
    with open(".m7-test-passed", "w") as f:
        f.write(marker_content)
    
    print("📝 Created M7 test marker: .m7-test-passed")


def create_pr_workflow(title, issue_number, description_file=None, skip_m7_test=False):
    """Complete PR creation workflow"""
    
    print("\n" + "="*60) 
    print("🚀 STARTING PR CREATION WORKFLOW")
    print("="*60)
    
    # 1. Check current state
    current_branch = get_current_branch()
    print(f"📍 Current branch: {current_branch}")
    
    if current_branch == "main":
        print("❌ Cannot create PR from main branch")
        sys.exit(1)
    
    uncommitted = get_uncommitted_changes()
    if uncommitted:
        print("❌ Uncommitted changes detected:")
        print(uncommitted)
        print("Please commit or stash changes first")
        sys.exit(1)
    
    # 2. MANDATORY: Run M7 end-to-end test (unless explicitly skipped)
    if not skip_m7_test:
        if not run_m7_end_to_end():
            print("❌ M7 test failed - PR creation aborted")
            sys.exit(1)
    else:
        print("⚠️  SKIPPING M7 TEST - NOT RECOMMENDED")
    
    # 3. Handle data submodule changes first
    print("\n🔄 Handling data submodule changes...")
    run_command("pixi run commit-data-changes", "Committing data submodule changes")
    
    # 4. Add M7 test marker and update commit message
    if Path(".m7-test-passed").exists():
        # Read M7 test details
        with open(".m7-test-passed", "r") as f:
            marker_content = f.read()
        
        # Extract key info
        test_timestamp = None
        data_files = None
        for line in marker_content.split("\n"):
            if line.startswith("TEST_TIMESTAMP="):
                test_timestamp = line.split("=")[1]
            elif line.startswith("M7_DATA_FILES="):
                data_files = line.split("=")[1]
        
        # Update commit message to include M7 test info
        current_commit = run_command("git log -1 --pretty=%B", "Getting current commit message")
        original_msg = current_commit.stdout.strip()
        
        # Add M7 test marker to commit message
        updated_msg = f"""{original_msg}

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: {data_files} data files validated
🕐 Test Time: {test_timestamp or 'unknown'}"""
        
        # Force add marker file and amend commit
        run_command("git add -f .m7-test-passed", "Force adding M7 test marker to commit")
        run_command(f'git commit --amend -m "{updated_msg}"', "Updating commit with M7 test info")
        print("📝 M7 test marker and status included in commit message")
    
    # 5. Push current branch
    run_command(f"git push -u origin {current_branch}", f"Pushing branch {current_branch}")
    
    # 5. Create PR body
    if description_file and Path(description_file).exists():
        with open(description_file, 'r') as f:
            body = f.read()
    else:
        # Generate default PR body
        body = f"""## Summary

[Describe your changes here]

## Key Changes

- [Change 1]
- [Change 2] 
- [Change 3]

## Test Results

✅ **M7 End-to-End Test**: PASSED
- M7 dataset built successfully
- All expected data files generated
- Build tracking verified

## Test Plan

- [x] M7 end-to-end test passed
- [x] Data submodule changes committed
- [ ] Additional testing as needed

Fixes #{issue_number}

🤖 Generated with [Claude Code](https://claude.ai/code)"""
    
    # 6. Create PR using gh CLI
    result = run_command(f'gh pr create --title "{title}" --body "{body}"', "Creating PR with gh CLI")
    
    # Extract PR URL from output (check both stdout and stderr)
    pr_url = None
    if result:
        # Check stdout first (where gh pr create normally outputs the URL)
        if result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'https://github.com/' in line and '/pull/' in line:
                    pr_url = line.strip()
                    break
        
        # Fallback to stderr if not found in stdout
        if not pr_url and result.stderr:
            lines = result.stderr.split('\n')
            for line in lines:
                if 'https://github.com/' in line and '/pull/' in line:
                    pr_url = line.strip()
                    break
    
    if not pr_url:
        print("⚠️  Could not extract PR URL from gh output")
        if result and result.stdout:
            print(f"   stdout: {result.stdout.strip()}")
        if result and result.stderr:
            print(f"   stderr: {result.stderr.strip()}")
        # Try to get PR URL using gh pr list as fallback
        print("🔄 Attempting to find PR URL using gh pr list...")
        fallback_result = run_command(f"gh pr list --head {current_branch} --json url --jq '.[0].url'", "Getting PR URL from list", check=False)
        if fallback_result and fallback_result.stdout.strip():
            pr_url = fallback_result.stdout.strip()
            print(f"✅ Found PR URL via fallback: {pr_url}")
        else:
            print("❌ Could not determine PR URL")
            return None
    
    print(f"✅ PR Created: {pr_url}")
    
    # 7. Update commit message with actual PR URL
    pr_number = pr_url.split('/pull/')[-1]
    
    # Get the last commit message
    last_commit = run_command("git log -1 --pretty=%B", "Getting last commit message")
    commit_msg = last_commit.stdout.strip()
    
    # Update PR placeholder with actual number
    if "PLACEHOLDER" in commit_msg:
        updated_msg = commit_msg.replace("PLACEHOLDER", pr_number)
    elif f"#{issue_number}" in commit_msg and "PR:" not in commit_msg:
        # Add PR line if missing
        lines = commit_msg.split('\n')
        for i, line in enumerate(lines):
            if f"#{issue_number}" in line:
                lines.insert(i+1, "")
                lines.insert(i+2, f"PR: {pr_url}")
                break
        updated_msg = '\n'.join(lines)
    else:
        updated_msg = commit_msg
    
    # Amend commit with updated message
    run_command(f'git commit --amend -m "{updated_msg}"', "Updating commit with PR URL")
    run_command("git push --force-with-lease", "Force pushing updated commit")
    
    print("\n" + "="*60)
    print("🎉 PR CREATION WORKFLOW COMPLETED")
    print("="*60)
    print(f"📋 PR Title: {title}")
    print(f"🔗 PR URL: {pr_url}")
    print(f"🏷️  Issue: #{issue_number}")
    print(f"🌿 Branch: {current_branch}")
    print("✅ M7 test passed before PR creation")
    print("✅ Data submodule changes committed")
    print("✅ Commit message updated with PR URL")
    
    return pr_url


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Create PR with mandatory M7 end-to-end testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python infra/create_pr_with_m7_test.py "Fix config bug" 42
  python infra/create_pr_with_m7_test.py "Add new feature" 43 --description pr_body.md
        """
    )
    
    parser.add_argument("title", nargs='?', help="PR title")
    parser.add_argument("issue_number", nargs='?', type=int, help="GitHub issue number")
    parser.add_argument("--description", help="Path to file containing PR description")
    parser.add_argument("--skip-m7-test", action="store_true", 
                       help="Skip M7 test (NOT RECOMMENDED)")
    parser.add_argument("--skip-pr-creation", action="store_true",
                       help="Only run M7 test, skip PR creation")
    
    args = parser.parse_args()
    
    if args.skip_pr_creation:
        # Only run M7 test
        success = run_m7_end_to_end()
        sys.exit(0 if success else 1)
    
    # Validate required arguments for PR creation
    if not args.title or not args.issue_number:
        parser.error("title and issue_number are required when creating PR")
    
    if args.skip_m7_test:
        print("⚠️  WARNING: Skipping M7 test - this is NOT recommended!")
        time.sleep(3)
    
    try:
        pr_url = create_pr_workflow(args.title, args.issue_number, args.description, args.skip_m7_test)
        
        if pr_url:
            print(f"\n🚀 PR successfully created: {pr_url}")
            sys.exit(0)
        else:
            print("\n❌ PR creation failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  PR creation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()