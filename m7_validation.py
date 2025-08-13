#!/usr/bin/env python3
"""
M7验证系统 - 检查4个核心条件
用于本地测试和GitHub Actions
"""

import datetime
import re
import subprocess
import sys
from typing import Dict, Any, Optional, List, Tuple


def get_commit_info() -> Dict[str, Any]:
    """获取commit信息"""
    try:
        # 获取commit message
        result = subprocess.run(['git', 'log', '-1', '--pretty=%B'], 
                              capture_output=True, text=True, check=True)
        commit_msg = result.stdout.strip()
        
        # 获取commit时间戳
        result = subprocess.run(['git', 'log', '-1', '--pretty=%ct'], 
                              capture_output=True, text=True, check=True)
        commit_time = int(result.stdout.strip())
        
        return {
            'message': commit_msg,
            'timestamp': commit_time,
            'datetime': datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc)
        }
    except Exception as e:
        print(f"❌ 获取commit信息失败: {e}")
        return {}


def check_condition_1_test_run(commit_msg: str) -> bool:
    """条件1: 跑了测试 (M7-TESTED标记检查)"""
    print("🔍 检查条件1: 是否运行了M7测试")
    
    if "M7-TESTED" in commit_msg and "This commit passed M7 end-to-end testing" in commit_msg:
        print("✅ 条件1通过: 找到M7测试标记")
        return True
    else:
        print("❌ 条件1失败: 没有找到M7测试标记")
        print("   期望模式: M7-TESTED: This commit passed M7 end-to-end testing")
        return False


def extract_test_time(commit_msg: str) -> Optional[datetime.datetime]:
    """从commit message中提取测试时间"""
    # 查找测试时间行
    for line in commit_msg.split('\n'):
        if "Test Time:" in line:
            # 提取ISO时间戳 (格式: 2025-08-13T11:27:36Z)
            time_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', line)
            if time_match:
                try:
                    return datetime.datetime.fromisoformat(time_match.group(1).replace('Z', '+00:00'))
                except:
                    pass
    return None


def check_condition_2_test_timing(commit_msg: str, commit_time: datetime.datetime) -> bool:
    """条件2: 测试时间在10分钟内"""
    print("🔍 检查条件2: 测试时间验证 (10分钟内)")
    
    test_time = extract_test_time(commit_msg)
    if not test_time:
        print("❌ 条件2失败: 无法提取测试时间")
        return False
    
    time_diff = (commit_time - test_time).total_seconds()
    time_diff_min = time_diff / 60
    
    print(f"   测试时间: {test_time}")
    print(f"   提交时间: {commit_time}")
    print(f"   时间差: {time_diff:.0f}秒 ({time_diff_min:.1f}分钟)")
    
    # 测试时间应该在commit时间前10分钟到后2分钟内
    if time_diff > 600:  # 10分钟
        print(f"❌ 条件2失败: 测试时间太早 ({time_diff_min:.1f}分钟前)")
        print("   测试必须在commit前10分钟内完成")
        return False
    elif time_diff < -120:  # -2分钟  
        print(f"❌ 条件2失败: 测试时间太晚 ({-time_diff_min:.1f}分钟后)")
        print("   这表明时钟同步问题或无效时间戳")
        return False
    else:
        print("✅ 条件2通过: 测试时间在合理范围内")
        if time_diff < 0:
            print(f"   注意: 测试在commit后运行 (常见于--amend操作)")
        return True


def check_condition_3_commit_freshness(commit_time: datetime.datetime) -> bool:
    """条件3: commit在24小时内"""
    print("🔍 检查条件3: commit新鲜度验证 (24小时内)")
    
    now = datetime.datetime.now(datetime.timezone.utc)
    time_diff = (now - commit_time).total_seconds()
    hours_diff = time_diff / 3600
    
    print(f"   当前时间: {now}")
    print(f"   提交时间: {commit_time}")
    print(f"   时间差: {hours_diff:.1f}小时")
    
    if hours_diff > 24:
        print(f"❌ 条件3失败: commit太旧 ({hours_diff:.1f}小时前)")
        print("   Commit必须在24小时内")
        return False
    else:
        print("✅ 条件3通过: commit在24小时内")
        return True


def check_condition_4_test_results(commit_msg: str) -> bool:
    """条件4: 测试结果充足 (≥7个数据文件)"""
    print("🔍 检查条件4: 测试结果验证 (M7数据充足性)")
    
    if "Test Results:" in commit_msg and "data files validated" in commit_msg:
        # 提取文件数量
        for line in commit_msg.split('\n'):
            if "Test Results:" in line:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    file_count = int(numbers[0])
                    print(f"   发现测试结果: {file_count} 个数据文件")
                    if file_count >= 7:  # M7至少7个文件
                        print(f"✅ 条件4通过: 验证了{file_count}个数据文件 (≥7)")
                        return True
                    else:
                        print(f"❌ 条件4失败: 数据文件不足 ({file_count} < 7)")
                        return False
        print("❌ 条件4失败: 无法解析测试结果数量")
        return False
    else:
        print("❌ 条件4失败: 没有找到测试结果")
        print("   期望模式: Test Results: X data files validated")
        return False


def validate_commit() -> bool:
    """验证当前commit的所有4个条件"""
    print("="*60)
    print("🔍 M7验证开始 - 检查4个核心条件")
    print("1. ✅ 跑了测试")
    print("2. ⏰ 测试通过的结束时间在push时间10分钟之内")
    print("3. 📅 push时间在24h内")
    print("4. 📊 CI上跑简易测试是通的")
    print("="*60)
    
    # 获取commit信息
    commit_info = get_commit_info()
    if not commit_info:
        return False
    
    print(f"\n📝 Commit信息:")
    print(f"   时间: {commit_info['datetime']}")
    print(f"   消息长度: {len(commit_info['message'])}字符")
    print()
    
    # 运行所有检查
    checks = []
    
    # 检查1: 跑了测试
    checks.append(check_condition_1_test_run(commit_info['message']))
    print()
    
    # 检查2: 测试时间
    checks.append(check_condition_2_test_timing(commit_info['message'], commit_info['datetime']))
    print()
    
    # 检查3: commit新鲜度
    checks.append(check_condition_3_commit_freshness(commit_info['datetime']))
    print()
    
    # 检查4: 测试结果
    checks.append(check_condition_4_test_results(commit_info['message']))
    print()
    
    # 总结
    passed = sum(checks)
    total = len(checks)
    
    print("="*60)
    if all(checks):
        print(f"🎉 所有检查通过! ({passed}/{total})")
        print("✅ 这个commit可以安全合并")
        return True
    else:
        print(f"❌ 检查失败! ({passed}/{total})")
        print("🚫 这个commit不应该被合并")
        return False


def test_scenarios():
    """测试各种场景的正例和反例"""
    print("🧪 测试M7验证逻辑 - 正例和反例")
    print("="*50)
    
    test_cases = [
        # 正例
        {
            "name": "✅ 正例: 完整有效的commit",
            "message": """Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: 418 data files validated
🕐 Test Time: 2025-08-13T11:57:00Z""",
            "commit_time": datetime.datetime(2025, 8, 13, 12, 0, 0, tzinfo=datetime.timezone.utc),
            "expected": True
        },
        
        # 反例1: 没有M7标记
        {
            "name": "❌ 反例1: 没有M7验证标记",
            "message": """Fix some bug

This is a regular commit without M7 validation.""",
            "commit_time": datetime.datetime(2025, 8, 13, 12, 0, 0, tzinfo=datetime.timezone.utc),
            "expected": False
        },
        
        # 反例2: 没有测试结果
        {
            "name": "❌ 反例2: 有M7标记但没有测试结果",
            "message": """Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
🕐 Test Time: 2025-08-13T11:57:00Z

But no test results included.""",
            "commit_time": datetime.datetime(2025, 8, 13, 12, 0, 0, tzinfo=datetime.timezone.utc),
            "expected": False
        },
        
        # 反例3: 测试文件数量不足
        {
            "name": "❌ 反例3: 测试文件数量不足",
            "message": """Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: 3 data files validated
🕐 Test Time: 2025-08-13T11:57:00Z""",
            "commit_time": datetime.datetime(2025, 8, 13, 12, 0, 0, tzinfo=datetime.timezone.utc),
            "expected": False
        },
        
        # 反例4: 测试时间太早
        {
            "name": "❌ 反例4: 测试时间太早(15分钟前)",
            "message": """Fix Issue #80: Some fix

✅ M7-TESTED: This commit passed M7 end-to-end testing
📊 Test Results: 418 data files validated
🕐 Test Time: 2025-08-13T11:45:00Z""",
            "commit_time": datetime.datetime(2025, 8, 13, 12, 0, 0, tzinfo=datetime.timezone.utc),
            "expected": False
        }
    ]
    
    all_passed = True
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 测试场景{i}: {case['name']}")
        
        # 运行检查
        results = []
        results.append(check_condition_1_test_run(case['message']))
        results.append(check_condition_2_test_timing(case['message'], case['commit_time']))
        results.append(check_condition_3_commit_freshness(case['commit_time']))
        results.append(check_condition_4_test_results(case['message']))
        
        actual = all(results)
        expected = case['expected']
        
        if actual == expected:
            print(f"✅ 测试通过: 期望{expected}, 实际{actual}")
        else:
            print(f"❌ 测试失败: 期望{expected}, 实际{actual}")
            all_passed = False
        
        print("-" * 30)
    
    print(f"\n🎯 测试总结: {'全部通过' if all_passed else '有失败'}")
    return all_passed


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 运行测试模式
        success = test_scenarios()
        sys.exit(0 if success else 1)
    else:
        # 运行验证模式
        success = validate_commit()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
