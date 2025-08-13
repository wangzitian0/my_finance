#!/usr/bin/env python3
"""
CI M7 Validation Script - Pure 4-condition validation logic
Used in GitHub Actions, no test logic included
"""

import datetime
import re
import subprocess
import sys
from typing import Optional


def get_commit_info():
    """Get commit information - check actual PR commits, not merge commit"""
    import os
    
    try:
        # In GitHub Actions, check if we have PR-specific environment variables
        github_sha = os.environ.get('GITHUB_SHA')
        github_event_name = os.environ.get('GITHUB_EVENT_NAME')
        
        if github_event_name == 'pull_request' and github_sha:
            # In PR context, GitHub_SHA is the merge commit
            # We need to find the actual PR branch head
            print("🔍 GitHub Actions PR context detected...")
            
            # Check if current HEAD is a merge commit
            result = subprocess.run(['git', 'log', '-1', '--pretty=%P'], 
                                  capture_output=True, text=True, check=True)
            parents = result.stdout.strip().split()
            
            if len(parents) > 1:
                print("🔍 Found merge commit, getting PR branch commits...")
                print(f"🔍 Merge parents: {parents}")
                
                # Try different approaches to get PR commits
                git_commands = [
                    f'{parents[0]}..HEAD^',  # Original approach
                    f'{parents[1]}..HEAD^',  # Try second parent
                    f'{parents[0]}..{parents[1]}',  # Between parents
                ]
                
                pr_commits = []
                for cmd in git_commands:
                    try:
                        print(f"🔍 Trying git log command: {cmd}")
                        result = subprocess.run(['git', 'log', '--pretty=%H', cmd], 
                                              capture_output=True, text=True, check=True)
                        commits = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                        print(f"🔍 Found {len(commits)} commits: {commits[:3] if commits else 'none'}")
                        if commits:
                            pr_commits = commits
                            break
                    except Exception as e:
                        print(f"🔍 Command failed: {e}")
                        continue
                
                if pr_commits:
                    # Use the most recent commit from the PR
                    latest_pr_commit = pr_commits[0]
                    print(f"🔍 Checking latest PR commit: {latest_pr_commit[:8]}")
                    
                    # Get commit message from the actual PR commit
                    result = subprocess.run(['git', 'log', '-1', '--pretty=%B', latest_pr_commit], 
                                          capture_output=True, text=True, check=True)
                    commit_msg = result.stdout.strip()
                    
                    # Get commit timestamp from the actual PR commit
                    result = subprocess.run(['git', 'log', '-1', '--pretty=%ct', latest_pr_commit], 
                                          capture_output=True, text=True, check=True)
                    commit_time = int(result.stdout.strip())
                    
                    return commit_msg, commit_time
                else:
                    print("🔍 No PR commits found, falling back to HEAD")
        
        # Not in PR context or no merge commit detected, use HEAD
        print("🔍 Using HEAD commit...")
        
        # Get commit message
        result = subprocess.run(['git', 'log', '-1', '--pretty=%B'], 
                              capture_output=True, text=True, check=True)
        commit_msg = result.stdout.strip()
        
        # Get commit timestamp
        result = subprocess.run(['git', 'log', '-1', '--pretty=%ct'], 
                              capture_output=True, text=True, check=True)
        commit_time = int(result.stdout.strip())
        
        return commit_msg, commit_time
    except Exception as e:
        print(f"❌ Failed to get commit info: {e}")
        sys.exit(1)


def check_condition_1_test_run(commit_msg: str) -> bool:
    """Condition 1: Tests were run"""
    print("🔍 Checking condition 1: M7 tests were executed")
    
    if "M7-TESTED" in commit_msg and "This commit passed M7 end-to-end testing" in commit_msg:
        print("✅ Condition 1 passed: Found M7 test marker")
        return True
    else:
        print("❌ Condition 1 failed: M7 test marker not found")
        print("   Expected pattern: M7-TESTED: This commit passed M7 end-to-end testing")
        print("   Please use: p3 create-pr \"title\" ISSUE_NUMBER")
        return False


def extract_test_time(commit_msg: str) -> Optional[datetime.datetime]:
    """Extract test time from commit message"""
    for line in commit_msg.split('\n'):
        if "Test Time:" in line:
            time_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', line)
            if time_match:
                try:
                    return datetime.datetime.fromisoformat(time_match.group(1).replace('Z', '+00:00'))
                except:
                    pass
    return None


def check_condition_2_test_timing(commit_msg: str, commit_time: int) -> bool:
    """Condition 2: Test time within 10 minutes of commit time"""
    print("🔍 Checking condition 2: Test timing validation (within 10 minutes)")
    
    test_time = extract_test_time(commit_msg)
    if not test_time:
        print("❌ Condition 2 failed: Cannot extract test time")
        return False
    
    commit_dt = datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc)
    time_diff = (commit_dt - test_time).total_seconds()
    time_diff_min = time_diff / 60
    
    print(f"   Test time: {test_time}")
    print(f"   Commit time: {commit_dt}")
    print(f"   Time difference: {time_diff:.0f}s ({time_diff_min:.1f}min)")
    
    if time_diff > 600:  # 10 minutes
        print(f"❌ Condition 2 failed: Test too early ({time_diff_min:.1f}min ago)")
        print("   Tests must complete within 10 minutes before commit")
        return False
    elif time_diff < -120:  # -2 minutes  
        print(f"❌ Condition 2 failed: Test too late ({-time_diff_min:.1f}min after)")
        return False
    else:
        print("✅ Condition 2 passed: Test timing is within acceptable range")
        return True


def check_condition_3_commit_freshness(commit_time: int) -> bool:
    """Condition 3: Commit within 24 hours"""
    print("🔍 Checking condition 3: Commit freshness validation (within 24 hours)")
    
    now = datetime.datetime.now(datetime.timezone.utc)
    commit_dt = datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc)
    time_diff = (now - commit_dt).total_seconds()
    hours_diff = time_diff / 3600
    
    print(f"   Current time: {now}")
    print(f"   Commit time: {commit_dt}")
    print(f"   Time difference: {hours_diff:.1f}h")
    
    if hours_diff > 24:
        print(f"❌ Condition 3 failed: Commit too old ({hours_diff:.1f}h ago)")
        print("   Commit must be within 24 hours")
        return False
    else:
        print("✅ Condition 3 passed: Commit is within 24 hours")
        return True


def check_condition_4_test_results(commit_msg: str) -> bool:
    """Condition 4: Sufficient test results (≥7 data files)"""
    print("🔍 Checking condition 4: Test results validation (M7 data sufficiency)")
    
    if "Test Results:" in commit_msg and "data files validated" in commit_msg:
        for line in commit_msg.split('\n'):
            if "Test Results:" in line:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    file_count = int(numbers[0])
                    print(f"   Found test results: {file_count} data files")
                    if file_count >= 7:
                        print(f"✅ Condition 4 passed: Validated {file_count} data files (≥7)")
                        return True
                    else:
                        print(f"❌ Condition 4 failed: Insufficient data files ({file_count} < 7)")
                        return False
        print("❌ Condition 4 failed: Cannot parse test results count")
        return False
    else:
        print("❌ Condition 4 failed: Test results not found")
        print("   Expected pattern: Test Results: X data files validated")
        return False


def main():
    """Main validation function - CI only"""
    print("🔍 M7 Validation Starting - Checking 4 Core Conditions")
    print("1. ✅ Tests were run")
    print("2. ⏰ Test completion time within 10 minutes of push time")  
    print("3. 📅 Push time within 24h")
    print("4. 📊 Simple tests pass on CI")
    print("="*60)
    
    # Get commit info
    commit_msg, commit_time = get_commit_info()
    
    print(f"📝 Commit time: {datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc)}")
    print(f"📝 Message length: {len(commit_msg)} characters")
    
    # Debug: Show first few lines of commit message for troubleshooting
    lines = commit_msg.split('\n')
    print(f"📝 First line: {lines[0]}")
    if len(lines) > 1:
        print(f"📝 Total lines: {len(lines)}")
        for i, line in enumerate(lines[1:6], 1):  # Show lines 1-5
            print(f"📝 Line {i}: {line}")
    print()
    
    # Run all checks
    checks = [
        check_condition_1_test_run(commit_msg),
        check_condition_2_test_timing(commit_msg, commit_time),
        check_condition_3_commit_freshness(commit_time),
        check_condition_4_test_results(commit_msg)
    ]
    
    passed = sum(checks)
    total = len(checks)
    
    print("="*60)
    if all(checks):
        print(f"🎉 All checks passed! ({passed}/{total})")
        print("✅ This commit can be safely merged")
        sys.exit(0)
    else:
        print(f"❌ Checks failed! ({passed}/{total})")
        print("🚫 This commit should not be merged")
        print()
        print("📝 Fix steps:")
        print("1. Run: p3 e2e")
        print("2. Use: p3 create-pr \"title\" ISSUE_NUMBER")
        sys.exit(1)


if __name__ == "__main__":
    main()