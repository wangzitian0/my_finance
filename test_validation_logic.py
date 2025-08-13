#!/usr/bin/env python3
"""
本地测试M7验证逻辑
测试4个核心条件：
1. 跑了测试
2. 测试通过的结束时间在push时间10分钟之内
3. push时间在24h内
4. CI上跑简易测试是通的
"""

import datetime
import subprocess
import sys
from typing import Dict, Any, Optional


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


def check_test_run(commit_msg: str) -> bool:
    """检查条件1: 跑了测试"""
    print("🔍 检查条件1: 跑了测试")
    
    if "M7-TESTED" in commit_msg and "This commit passed M7 end-to-end testing" in commit_msg:
        print("✅ 条件1通过: 找到M7测试标记")
        return True
    else:
        print("❌ 条件1失败: 没有找到M7测试标记")
        print("   期望: M7-TESTED: This commit passed M7 end-to-end testing")
        return False


def extract_test_time(commit_msg: str) -> Optional[datetime.datetime]:
    """从commit message中提取测试时间"""
    lines = commit_msg.split('\n')
    for line in lines:
        if "🕐 Test Time:" in line or "Test Time:" in line:
            # 提取ISO时间戳 (格式: 2025-08-13T11:27:36Z)
            parts = line.split("Test Time:")
            if len(parts) >= 2:
                time_str = parts[1].strip()
                # 清理可能的额外字符
                import re
                time_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', time_str)
                if time_match:
                    try:
                        return datetime.datetime.fromisoformat(time_match.group(1).replace('Z', '+00:00'))
                    except:
                        pass
    return None


def check_test_timing(commit_msg: str, commit_time: datetime.datetime) -> bool:
    """检查条件2: 测试通过的结束时间在push时间10分钟之内"""
    print("🔍 检查条件2: 测试时间在commit时间10分钟内")
    
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
        print("   测试不能比commit晚超过2分钟")
        return False
    else:
        print("✅ 条件2通过: 测试时间在合理范围内")
        return True


def check_commit_freshness(commit_time: datetime.datetime) -> bool:
    """检查条件3: push时间在24h内"""
    print("🔍 检查条件3: commit时间在24小时内")
    
    now = datetime.datetime.now(datetime.timezone.utc)
    time_diff = (now - commit_time).total_seconds()
    hours_diff = time_diff / 3600
    
    print(f"   当前时间: {now}")
    print(f"   提交时间: {commit_time}")
    print(f"   时间差: {hours_diff:.1f}小时")
    
    if hours_diff > 24:
        print(f"❌ 条件3失败: commit太旧 ({hours_diff:.1f}小时前)")
        print("   commit必须在24小时内")
        return False
    else:
        print("✅ 条件3通过: commit在24小时内")
        return True


def check_test_results(commit_msg: str) -> bool:
    """检查条件4: 测试结果通过"""
    print("🔍 检查条件4: 测试结果通过")
    
    if "Test Results:" in commit_msg and "data files validated" in commit_msg:
        # 提取文件数量
        lines = commit_msg.split('\n')
        for line in lines:
            if "Test Results:" in line:
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    file_count = int(numbers[0])
                    print(f"   验证了 {file_count} 个数据文件")
                    if file_count >= 7:  # M7至少7个文件
                        print("✅ 条件4通过: 测试结果充足")
                        return True
                    else:
                        print(f"❌ 条件4失败: 数据文件不足 ({file_count} < 7)")
                        return False
        print("❌ 条件4失败: 无法解析测试结果数量")
        return False
    else:
        print("❌ 条件4失败: 没有找到测试结果")
        return False


def main():
    """主测试函数"""
    print("="*60)
    print("🧪 M7验证逻辑本地测试")
    print("="*60)
    
    # 获取commit信息
    commit_info = get_commit_info()
    if not commit_info:
        sys.exit(1)
    
    print(f"\n📝 Commit信息:")
    print(f"   时间: {commit_info['datetime']}")
    print(f"   消息长度: {len(commit_info['message'])}字符")
    print()
    
    # 运行所有检查
    checks = []
    
    # 检查1: 跑了测试
    checks.append(check_test_run(commit_info['message']))
    print()
    
    # 检查2: 测试时间
    checks.append(check_test_timing(commit_info['message'], commit_info['datetime']))
    print()
    
    # 检查3: commit新鲜度
    checks.append(check_commit_freshness(commit_info['datetime']))
    print()
    
    # 检查4: 测试结果
    checks.append(check_test_results(commit_info['message']))
    print()
    
    # 总结
    print("="*60)
    passed = sum(checks)
    total = len(checks)
    
    if all(checks):
        print(f"🎉 所有检查通过! ({passed}/{total})")
        print("✅ 这个commit可以安全合并")
        sys.exit(0)
    else:
        print(f"❌ 检查失败! ({passed}/{total})")
        print("🚫 这个commit不应该被合并")
        sys.exit(1)


if __name__ == "__main__":
    main()
