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
        github_sha = os.environ.get("GITHUB_SHA")
        github_event_name = os.environ.get("GITHUB_EVENT_NAME")

        if github_event_name == "pull_request" and github_sha:
            # In PR context, GitHub_SHA is the merge commit
            # We need to find the actual PR branch head
            print("🔍 GitHub Actions PR context detected...")

            # Check if current HEAD is a merge commit
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%P"], capture_output=True, text=True, check=True
            )
            parents = result.stdout.strip().split()

            if len(parents) > 1:
                print("🔍 Found merge commit, getting PR branch commits...")
                print(f"🔍 Merge parents: {parents}")

                # Try different approaches to get PR commits
                git_commands = [
                    f"{parents[0]}..HEAD^",  # Original approach
                    f"{parents[1]}..HEAD^",  # Try second parent
                    f"{parents[0]}..{parents[1]}",  # Between parents
                ]

                pr_commits = []
                for cmd in git_commands:
                    try:
                        print(f"🔍 Trying git log command: {cmd}")
                        result = subprocess.run(
                            ["git", "log", "--pretty=%H", cmd],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        commits = [
                            line.strip()
                            for line in result.stdout.strip().split("\n")
                            if line.strip()
                        ]
                        print(
                            f"🔍 Found {len(commits)} commits: {commits[:3] if commits else 'none'}"
                        )
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
                    result = subprocess.run(
                        ["git", "log", "-1", "--pretty=%B", latest_pr_commit],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    commit_msg = result.stdout.strip()

                    # Get commit timestamp from the actual PR commit
                    result = subprocess.run(
                        ["git", "log", "-1", "--pretty=%ct", latest_pr_commit],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    commit_time = int(result.stdout.strip())

                    return commit_msg, commit_time
                else:
                    print("🔍 No PR commits found, falling back to HEAD")

        # Not in PR context or no merge commit detected, use HEAD
        print("🔍 Using HEAD commit...")

        # Get commit message
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True
        )
        commit_msg = result.stdout.strip()

        # Get commit timestamp
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%ct"], capture_output=True, text=True, check=True
        )
        commit_time = int(result.stdout.strip())

        return commit_msg, commit_time
    except Exception as e:
        print(f"❌ Failed to get commit info: {e}")
        sys.exit(1)


def check_condition_1_test_run(commit_msg: str) -> bool:
    """Condition 1: Tests were run (M7 or F2 fast-build accepted)"""
    print("🔍 检查条件1: 验证测试已执行")

    # Accept both M7 and F2 test markers
    has_m7_test = "M7-TESTED" in commit_msg and "This commit passed M7 end-to-end testing" in commit_msg
    has_f2_test = "F2-TESTED" in commit_msg and "This commit passed F2 fast-build testing" in commit_msg
    
    if has_m7_test:
        print("✅ 条件1通过: 发现M7完整测试标记")
        return True
    elif has_f2_test:
        print("✅ 条件1通过: 发现F2快速测试标记")
        return True
    else:
        print("❌ 条件1失败: 缺少有效的测试执行标记")
        print()
        print("🚨 错误: 此提交未使用规定的工作流程创建！")
        print()
        print("🔧 正确的工作流程:")
        print("   1. 运行测试: p3 e2e                      # 执行F2快速测试")
        print('   2. 创建PR: p3 create-pr "标题" 问题编号   # 自动验证并创建PR')
        print()
        print("❌ 禁止的方法 (CI会失败):")
        print("   • 直接 git push/commit")
        print("   • 手动通过GitHub界面创建PR")
        print("   • 手工编写测试标记")
        print("   • 绕过自动化脚本")
        print()
        print("📖 详见 CLAUDE.md 了解为什么手动方法会失败")
        return False


def extract_test_time(commit_msg: str) -> Optional[datetime.datetime]:
    """Extract test time from commit message"""
    for line in commit_msg.split("\n"):
        if "Test Time:" in line:
            time_match = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", line)
            if time_match:
                try:
                    return datetime.datetime.fromisoformat(
                        time_match.group(1).replace("Z", "+00:00")
                    )
                except:
                    pass
    return None


def check_condition_2_test_timing(commit_msg: str, commit_time: int) -> bool:
    """Condition 2: Test time within 10 minutes of commit time"""
    print("🔍 检查条件2: 测试时间验证 (10分钟内)")

    test_time = extract_test_time(commit_msg)
    if not test_time:
        print("❌ 条件2失败: 无法提取有效的测试时间戳")
        print()
        print("🚨 这表明测试标记是手工编写的或无效的！")
        print()
        print("✅ 解决方案: 使用自动化工作流程:")
        print("   1. p3 e2e                           # 真实测试会嵌入有效时间戳")
        print('   2. p3 create-pr "标题" 问题编号      # 正确的提交消息格式')
        return False

    commit_dt = datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc)
    time_diff = (commit_dt - test_time).total_seconds()
    time_diff_min = time_diff / 60

    print(f"   Test time: {test_time}")
    print(f"   Commit time: {commit_dt}")
    print(f"   Time difference: {time_diff:.0f}s ({time_diff_min:.1f}min)")

    if time_diff > 600:  # 10 minutes
        print(f"❌ 条件2失败: 测试时间戳过早 ({time_diff_min:.1f}分钟前)")
        print()
        print("🚨 这表明测试结果是虚假的或过时的！")
        print("✅ 解决方案: 在创建PR前立即运行新测试:")
        print("   1. p3 e2e                           # 新鲜的测试执行")
        print('   2. p3 create-pr "标题" 问题编号      # 立即创建PR')
        return False
    elif time_diff < -120:  # -2 minutes
        print(f"❌ 条件2失败: 测试时间戳过晚 ({-time_diff_min:.1f}分钟后)")
        print("🚨 这表明时间戳被篡改了！")
        return False
    else:
        print("✅ 条件2通过: 测试时间在可接受范围内")
        return True


def check_condition_3_commit_freshness(commit_time: int) -> bool:
    """Condition 3: Commit within 24 hours"""
    print("🔍 检查条件3: 提交新鲜度验证 (24小时内)")

    now = datetime.datetime.now(datetime.timezone.utc)
    commit_dt = datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc)
    time_diff = (now - commit_dt).total_seconds()
    hours_diff = time_diff / 3600

    print(f"   当前时间: {now}")
    print(f"   提交时间: {commit_dt}")
    print(f"   时间差: {hours_diff:.1f}小时")

    if hours_diff > 24:
        print(f"❌ 条件3失败: 提交过于陈旧 ({hours_diff:.1f}小时前)")
        print()
        print("🚨 此提交超过了24小时新鲜度要求！")
        print()
        print("✅ 解决方案: 使用自动化工作流程创建新提交:")
        print("   1. 做任何小的代码更改 (或运行 p3 format)")
        print("   2. p3 e2e                           # 新鲜的测试执行")
        print('   3. p3 create-pr "标题" 问题编号      # 24小时内的新提交')
        return False
    else:
        print("✅ 条件3通过: 提交在24小时内")
        return True


def check_condition_4_test_results(commit_msg: str) -> bool:
    """Condition 4: Sufficient test results (≥2 data files for F2)"""
    print("🔍 检查条件4: 测试结果验证 (数据充分性)")

    if "Test Results:" in commit_msg and "data files validated" in commit_msg:
        for line in commit_msg.split("\n"):
            if "Test Results:" in line:
                numbers = re.findall(r"\d+", line)
                if numbers:
                    file_count = int(numbers[0])
                    print(f"   发现测试结果: {file_count} 个数据文件")
                    # Accept both M7 (≥7 files) and F2 (≥2 files) test results
                    if file_count >= 2:
                        test_type = "M7完整测试" if file_count >= 7 else "F2快速测试"
                        print(f"✅ 条件4通过: 验证了 {file_count} 个数据文件 ({test_type})")
                        return True
                    else:
                        print(f"❌ 条件4失败: 数据文件不足 ({file_count} < 2)")
                        print()
                        print("🚨 这表明测试执行不完整！")
                        print()
                        print("✅ 解决方案: 运行正确的测试:")
                        print("   1. p3 e2e                           # F2快速测试验证")
                        print('   2. p3 create-pr "标题" 问题编号      # 正确的测试结果嵌入')
                        return False
        print("❌ 条件4失败: 无法解析测试结果数量")
        print("🚨 这表明测试标记已损坏或是手工编写的！")
        return False
    else:
        print("❌ 条件4失败: 未找到测试结果")
        print()
        print("🚨 这表明提交不是通过正确的测试创建的！")
        print()
        print("✅ 解决方案:")
        print("   1. p3 e2e                           # 执行真实的测试")
        print('   2. p3 create-pr "标题" 问题编号      # 在提交中嵌入测试结果')
        return False


def check_condition_5_code_formatting() -> bool:
    """Condition 5: Python code formatting with black and isort"""
    print("🔍 检查条件5: Python代码格式验证")

    try:
        # Install formatting tools if needed
        try:
            subprocess.run(
                ["python3", "-c", "import black, isort"], capture_output=True, check=True
            )
        except subprocess.CalledProcessError:
            print("   Installing black and isort...")
            subprocess.run(["pip", "install", "black", "isort"], capture_output=True, check=True)

        # Define project directories to check (avoid checking dependencies)
        project_dirs = [
            "ETL/",
            "dcf_engine/",
            "common/",
            "graph_rag/",
            "tests/",
            "infra/",
            "scripts/",
            "ci_m7_validation.py",
            "p3.py",
        ]

        # Check black formatting on project files only
        print("   Running black format check...")
        black_cmd = ["python3", "-m", "black", "--check", "--line-length", "100"] + project_dirs
        black_result = subprocess.run(black_cmd, capture_output=True, text=True)

        # Check isort formatting on project files only
        print("   Running isort format check...")
        isort_cmd = ["python3", "-m", "isort", "--check-only"] + project_dirs
        isort_result = subprocess.run(isort_cmd, capture_output=True, text=True)

        if black_result.returncode == 0 and isort_result.returncode == 0:
            print("✅ Condition 5 passed: Python code is properly formatted")
            return True
        else:
            print("❌ Condition 5 FAILED: Python code formatting issues found")
            print()
            if black_result.returncode != 0:
                print("🐍 Black formatting errors:")
                print(f"   {black_result.stderr}")
                print()
            if isort_result.returncode != 0:
                print("📦 Import sorting errors:")
                print(f"   {isort_result.stderr}")
                print()
            print("✅ SOLUTION: Fix formatting before creating PR:")
            print("   1. p3 format                        # Auto-fix all formatting")
            print("   2. p3 e2e                           # Validate after formatting")
            print('   3. p3 create-pr "title" ISSUE_NUMBER # Clean, formatted PR')
            return False

    except Exception as e:
        print(f"❌ Condition 5 FAILED: Error checking code formatting: {e}")
        print()
        print("🚨 This may indicate missing formatting tools or system issues!")
        print()
        print("✅ SOLUTION: Ensure clean environment:")
        print("   1. p3 activate                      # Ensure proper environment")
        print("   2. p3 format                        # Install and run formatters")
        return False


def main():
    """Main validation function - CI only"""
    print("🔍 CI测试验证开始 - 检查5个核心条件")
    print("1. ✅ 测试已执行 (M7或F2)")
    print("2. ⏰ 测试时间在推送时间10分钟内")
    print("3. 📅 推送时间在24小时内")
    print("4. 📊 CI上的简单测试通过")
    print("5. 🎨 Python代码格式验证")
    print("=" * 60)

    # Get commit info
    commit_msg, commit_time = get_commit_info()

    print(f"📝 Commit time: {datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc)}")
    print(f"📝 Message length: {len(commit_msg)} characters")

    # Debug: Show first few lines of commit message for troubleshooting
    lines = commit_msg.split("\n")
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
        check_condition_4_test_results(commit_msg),
        check_condition_5_code_formatting(),
    ]

    passed = sum(checks)
    total = len(checks)

    print("=" * 60)
    if all(checks):
        print(f"🎉 ALL M7 VALIDATION CHECKS PASSED! ({passed}/{total})")
        print("✅ This commit meets all quality requirements and can be safely merged")
        print("✅ The automated workflow was followed correctly")
        sys.exit(0)
    else:
        print(f"❌ M7 VALIDATION FAILED! ({passed}/{total} passed)")
        print("🚫 This commit does not meet quality requirements and should NOT be merged")
        print()
        print("🚨 ROOT CAUSE: This commit was not created using the required automated workflow")
        print()
        print("✅ COMPLETE SOLUTION (follow this exact sequence):")
        print("   1. p3 format                        # Fix any code formatting issues")
        print("   2. p3 e2e                           # Execute complete M7 testing")
        print('   3. p3 create-pr "Brief desc" ISSUE_NUM # Create/update PR with validation')
        print()
        print("❌ NEVER do these (they will always fail CI):")
        print("   • Direct git push/commit commands")
        print("   • Manual PR creation via GitHub UI")
        print("   • Hand-crafting M7-TESTED markers")
        print("   • Bypassing the p3 create-pr script")
        print()
        print("📖 For detailed explanation, see: CLAUDE.md (Why Manual Git Commands WILL FAIL CI)")
        sys.exit(1)


if __name__ == "__main__":
    main()
