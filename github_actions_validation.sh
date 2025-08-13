#!/bin/bash
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
