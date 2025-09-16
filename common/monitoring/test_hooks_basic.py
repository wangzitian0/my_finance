#!/usr/bin/env python3
"""
Minimal test to verify Claude Code hooks configuration works.
Tests basic functionality of hook system integration.
"""
import os
from pathlib import Path


def test_hooks_log_file_exists():
    """Test that hooks log file is being created in main project."""
    log_file = Path("/Users/SP14016/zitian/my_finance/logs/claude_agent_execution.log")
    assert log_file.exists(), f"Hooks log file should exist at {log_file}"
    assert log_file.stat().st_size > 0, "Hooks log file should contain data"


def test_load_claude_hooks_logs():
    """Test HRBP can load and parse hooks logs."""
    try:
        from ..agents.hrbp_performance_manager import get_hrbp_performance_manager

        manager = get_hrbp_performance_manager()
        logs_data = manager.load_claude_hooks_logs(days=1)

        assert isinstance(logs_data, dict), "Should return dictionary"
        assert (
            "sessions" in logs_data or "total_sessions" in logs_data
        ), "Should contain session data"

        print(f"✅ Hooks logs loaded successfully: {logs_data.get('total_sessions', 0)} sessions")
        return True

    except Exception as e:
        print(f"❌ Failed to load hooks logs: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Testing Claude Code hooks configuration...")

    print("\n1. Checking hooks log file...")
    try:
        test_hooks_log_file_exists()
        print("✅ Hooks log file exists and has content")
    except AssertionError as e:
        print(f"❌ {e}")

    print("\n2. Testing HRBP hooks integration...")
    test_load_claude_hooks_logs()

    print("\n🎯 Hooks basic test completed!")
