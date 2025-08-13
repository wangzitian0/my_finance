#!/usr/bin/env python3
"""
测试边界情况和失败场景
"""

import datetime
import tempfile
import os


def test_commit_message_scenarios():
    """测试不同的commit message场景"""
    print("🧪 测试commit message场景")
    
    # 从主测试脚本导入检查函数
    import sys
    sys.path.append('.')
    from test_validation_logic import check_test_run, check_test_timing, check_test_results
    
    # 测试场景1: 没有M7验证标记的commit
    test_msg_1 = """Fix some bug

This is a regular commit without M7 validation.
No testing information included."""
    
    print("\n📝 场景1: 没有M7验证标记")
    result1 = check_test_run(test_msg_1)
    assert not result1, "应该失败但通过了"
    print("✅ 正确拒绝了没有M7标记的commit")
    
    # 测试场景2: 有M7标记但没有测试结果
    test_msg_2 = """Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
🕐 Test Time: 2025-08-13T11:48:23Z

But no test results included."""
    
    print("\n📝 场景2: 有M7标记但没有测试结果")
    assert check_test_run(test_msg_2), "应该通过第一个检查"
    result2 = check_test_results(test_msg_2)
    assert not result2, "应该失败但通过了"
    print("✅ 正确拒绝了没有测试结果的commit")
    
    # 测试场景3: 测试文件数量不足
    test_msg_3 = """Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: 3 data files validated
🕐 Test Time: 2025-08-13T11:48:23Z"""
    
    print("\n📝 场景3: 测试文件数量不足")
    assert check_test_run(test_msg_3), "应该通过第一个检查"
    result3 = check_test_results(test_msg_3)
    assert not result3, "应该失败但通过了"
    print("✅ 正确拒绝了文件数量不足的commit")
    
    # 测试场景4: 测试时间太早
    now = datetime.datetime.now(datetime.timezone.utc)
    old_time = now - datetime.timedelta(minutes=15)  # 15分钟前
    test_msg_4 = f"""Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: 418 data files validated
🕐 Test Time: {old_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"""
    
    print("\n📝 场景4: 测试时间太早(15分钟前)")
    assert check_test_run(test_msg_4), "应该通过第一个检查"
    assert check_test_results(test_msg_4), "应该通过测试结果检查"
    result4 = check_test_timing(test_msg_4, now)
    assert not result4, "应该失败但通过了"
    print("✅ 正确拒绝了测试时间太早的commit")
    
    # 测试场景5: 完整有效的commit
    recent_time = now - datetime.timedelta(minutes=3)  # 3分钟前
    test_msg_5 = f"""Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: 418 data files validated
🕐 Test Time: {recent_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"""
    
    print("\n📝 场景5: 完整有效的commit")
    assert check_test_run(test_msg_5), "第一个检查应该通过"
    assert check_test_results(test_msg_5), "测试结果检查应该通过"
    result5 = check_test_timing(test_msg_5, now)
    assert result5, "时间检查应该通过"
    print("✅ 正确接受了有效的commit")
    
    print("\n🎉 所有边界情况测试通过!")


def test_github_actions_script():
    """生成GitHub Actions可以使用的脚本"""
    print("\n🔧 生成GitHub Actions验证脚本...")
    
    script_content = '''#!/bin/bash
set -e

echo "🔍 M7验证开始..."

# 获取commit信息
COMMIT_MSG=$(git log -1 --pretty=%B)
COMMIT_TIME=$(git log -1 --pretty=%ct)
CURRENT_TIME=$(date +%s)

echo "📝 Commit消息:"
echo "$COMMIT_MSG"
echo "---"

# 检查1: 跑了测试
echo "🔍 检查1: 是否运行了M7测试"
if echo "$COMMIT_MSG" | grep -q "M7-TESTED.*This commit passed M7 end-to-end testing"; then
    echo "✅ 检查1通过: 找到M7测试标记"
else
    echo "❌ 检查1失败: 没有找到M7测试标记"
    echo "   期望: M7-TESTED: This commit passed M7 end-to-end testing"
    exit 1
fi

# 检查2: 测试时间在10分钟内
echo "🔍 检查2: 测试时间验证"
TEST_TIME_LINE=$(echo "$COMMIT_MSG" | grep "🕐 Test Time:" | head -1)
if [ -z "$TEST_TIME_LINE" ]; then
    echo "❌ 检查2失败: 没有找到测试时间"
    exit 1
fi

# 提取ISO时间戳
TEST_TIME_ISO=$(echo "$TEST_TIME_LINE" | sed 's/.*Test Time: //' | grep -o '[0-9T:Z-]*')
if [ -z "$TEST_TIME_ISO" ]; then
    echo "❌ 检查2失败: 无法提取测试时间戳"
    exit 1
fi

# 转换为epoch时间
TEST_TIME_EPOCH=$(python3 -c "
import datetime
try:
    dt = datetime.datetime.fromisoformat('$TEST_TIME_ISO'.replace('Z', '+00:00'))
    print(int(dt.timestamp()))
except:
    print('0')
")

if [ "$TEST_TIME_EPOCH" -eq 0 ]; then
    echo "❌ 检查2失败: 无法解析测试时间"
    exit 1
fi

# 计算时间差
TIME_DIFF=$((COMMIT_TIME - TEST_TIME_EPOCH))
TIME_DIFF_MIN=$((TIME_DIFF / 60))

echo "   测试时间: $TEST_TIME_ISO"
echo "   时间差: ${TIME_DIFF}秒 (${TIME_DIFF_MIN}分钟)"

if [ "$TIME_DIFF" -gt 600 ]; then  # 10分钟
    echo "❌ 检查2失败: 测试时间太早 (${TIME_DIFF_MIN}分钟前)"
    exit 1
elif [ "$TIME_DIFF" -lt -120 ]; then  # -2分钟
    echo "❌ 检查2失败: 测试时间太晚 (${TIME_DIFF_MIN}分钟后)"
    exit 1
else
    echo "✅ 检查2通过: 测试时间在合理范围内"
fi

# 检查3: commit在24小时内
echo "🔍 检查3: commit新鲜度验证"
COMMIT_AGE=$((CURRENT_TIME - COMMIT_TIME))
COMMIT_AGE_HOURS=$((COMMIT_AGE / 3600))

if [ "$COMMIT_AGE" -gt 86400 ]; then  # 24小时
    echo "❌ 检查3失败: commit太旧 (${COMMIT_AGE_HOURS}小时前)"
    exit 1
else
    echo "✅ 检查3通过: commit在24小时内 (${COMMIT_AGE_HOURS}小时前)"
fi

# 检查4: 测试结果充足
echo "🔍 检查4: 测试结果验证"
if echo "$COMMIT_MSG" | grep -q "Test Results.*data files validated"; then
    FILE_COUNT=$(echo "$COMMIT_MSG" | grep "Test Results:" | grep -o '[0-9]*' | head -1)
    if [ -n "$FILE_COUNT" ] && [ "$FILE_COUNT" -ge 7 ]; then
        echo "✅ 检查4通过: 验证了${FILE_COUNT}个数据文件"
    else
        echo "❌ 检查4失败: 数据文件不足 (${FILE_COUNT:-0} < 7)"
        exit 1
    fi
else
    echo "❌ 检查4失败: 没有找到测试结果"
    exit 1
fi

echo "🎉 所有检查通过! 可以安全合并"
'''
    
    with open('github_actions_validation.sh', 'w') as f:
        f.write(script_content)
    
    print("✅ 生成了 github_actions_validation.sh")
    print("   可以在GitHub Actions中使用: bash github_actions_validation.sh")


if __name__ == "__main__":
    test_commit_message_scenarios()
    test_github_actions_script()
    print("\n🎉 所有测试完成!")
