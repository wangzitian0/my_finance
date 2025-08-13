#!/bin/bash
# 本地测试GitHub Actions脚本

echo "🧪 本地测试GitHub Actions工作流"
echo "================================"

# 从yaml文件中提取脚本部分并执行
# 这模拟了GitHub Actions的运行环境

set -e

echo "🔍 M7验证开始 - 检查4个核心条件..."
echo "1. ✅ 跑了测试"
echo "2. ⏰ 测试通过的结束时间在push时间10分钟之内"
echo "3. 📅 push时间在24h内"
echo "4. 📊 CI上跑简易测试是通的"
echo ""

# 获取commit信息
COMMIT_MSG=$(git log -1 --pretty=%B)
COMMIT_TIME=$(git log -1 --pretty=%ct)
CURRENT_TIME=$(date +%s)

echo "📝 Commit消息:"
echo "$COMMIT_MSG"
echo "---"
echo "📅 Commit时间: $(date -r $COMMIT_TIME -u 2>/dev/null || date -d @$COMMIT_TIME -u 2>/dev/null || python3 -c "import datetime; print(datetime.datetime.fromtimestamp($COMMIT_TIME, datetime.timezone.utc))")"
echo "📅 当前时间: $(date -u)"
echo ""

# 检查1: 跑了测试
echo "🔍 检查1: 是否运行了M7测试"
if echo "$COMMIT_MSG" | grep -q "M7-TESTED.*This commit passed M7 end-to-end testing"; then
    echo "✅ 检查1通过: 找到M7测试标记"
else
    echo "❌ 检查1失败: 没有找到M7测试标记"
    echo "   期望模式: M7-TESTED: This commit passed M7 end-to-end testing"
    echo ""
    echo "📝 修复步骤:"
    echo "   1. 运行: pixi run test-m7-e2e"
    echo "   2. 使用: pixi run create-pr \"标题\" ISSUE_NUMBER"
    exit 1
fi
echo ""

# 检查2: 测试时间在10分钟内
echo "🔍 检查2: 测试时间验证 (10分钟内)"
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

# 转换为epoch时间 (使用Python确保跨平台兼容)
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
    echo "   测试必须在commit前10分钟内完成"
    echo "   这防止在代码修改后使用过时的测试结果"
    exit 1
elif [ "$TIME_DIFF" -lt -120 ]; then  # -2分钟
    echo "❌ 检查2失败: 测试时间太晚 (${TIME_DIFF_MIN}分钟后)"
    echo "   这表明时钟同步问题或无效时间戳"
    exit 1
else
    echo "✅ 检查2通过: 测试时间在合理范围内"
    if [ "$TIME_DIFF" -lt 0 ]; then
        echo "   注意: 测试在commit后运行 (常见于--amend操作)"
    fi
fi
echo ""

# 检查3: commit在24小时内
echo "🔍 检查3: commit新鲜度验证 (24小时内)"
COMMIT_AGE=$((CURRENT_TIME - COMMIT_TIME))
COMMIT_AGE_HOURS=$((COMMIT_AGE / 3600))

echo "   Commit年龄: ${COMMIT_AGE}秒 (${COMMIT_AGE_HOURS}小时)"

if [ "$COMMIT_AGE" -gt 86400 ]; then  # 24小时
    echo "❌ 检查3失败: commit太旧 (${COMMIT_AGE_HOURS}小时前)"
    echo "   Commit必须在24小时内"
    echo "   请创建新的commit并重新测试"
    exit 1
else
    echo "✅ 检查3通过: commit在24小时内 (${COMMIT_AGE_HOURS}小时前)"
fi
echo ""

# 检查4: 测试结果充足
echo "🔍 检查4: 测试结果验证 (M7数据充足性)"
if echo "$COMMIT_MSG" | grep -q "Test Results.*data files validated"; then
    FILE_COUNT=$(echo "$COMMIT_MSG" | grep "Test Results:" | grep -o '[0-9]*' | head -1)
    echo "   发现测试结果: ${FILE_COUNT:-0} 个数据文件"
    
    if [ -n "$FILE_COUNT" ] && [ "$FILE_COUNT" -ge 7 ]; then
        echo "✅ 检查4通过: 验证了${FILE_COUNT}个数据文件 (≥7)"
    else
        echo "❌ 检查4失败: 数据文件不足 (${FILE_COUNT:-0} < 7)"
        echo "   M7测试需要至少7个公司的数据文件"
        exit 1
    fi
else
    echo "❌ 检查4失败: 没有找到测试结果"
    echo "   期望模式: Test Results: X data files validated"
    exit 1
fi
echo ""

# 成功总结
echo "🎉 所有4个核心条件检查通过!"
echo "✅ 1. 运行了M7测试"
echo "✅ 2. 测试时间在10分钟内"
echo "✅ 3. Commit在24小时内"
echo "✅ 4. 测试结果充足"
echo ""
echo "🚀 这个PR可以安全合并!"

echo ""
echo "📊 GitHub Actions摘要模拟:"
echo "## ✅ M7验证检查通过"
echo ""
echo "所有4个核心条件都满足:"
echo "- ✅ **M7测试运行**: 找到测试验证标记"
echo "- ✅ **测试时间**: 在commit前${TIME_DIFF_MIN}分钟 (≤10分钟)"
echo "- ✅ **Commit新鲜度**: ${COMMIT_AGE_HOURS}小时前 (≤24小时)"
echo "- ✅ **测试结果**: ${FILE_COUNT}个数据文件验证 (≥7)"
echo ""
echo "🚀 **这个PR已准备好合并!**"
