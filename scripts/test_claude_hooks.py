#!/usr/bin/env python3
"""
Test script for Claude Code hooks infrastructure

This script tests the hook manager and hook scripts to ensure they're working correctly.

Usage:
    python test_claude_hooks.py [--verbose]

GitHub Issue #214: Implement Claude Code hooks for comprehensive logging integration
"""

import argparse
import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Add common directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))

from monitoring.claude_hook_manager import get_hook_manager


def test_hook_manager():
    """Test the ClaudeHookManager directly."""
    print("Testing ClaudeHookManager...")
    
    hook_manager = get_hook_manager()
    
    # Test configuration loading
    status = hook_manager.get_hook_status()
    print(f"  ✓ Configuration loaded: {status['config_version']}")
    print(f"  ✓ Hooks enabled: {status['enabled']}")
    
    # Test session management
    session_id = hook_manager.start_session({"test": "session"})
    print(f"  ✓ Session started: {session_id}")
    
    # Test each hook type
    prompt_event_id = hook_manager.capture_user_prompt("Test prompt", {"source": "test"})
    print(f"  ✓ User prompt captured: {prompt_event_id}")
    
    tool_event_id = hook_manager.capture_tool_invocation(
        "TestTool", 
        {"param": "value"}, 
        {"result": "success"}, 
        100, 
        True
    )
    print(f"  ✓ Tool invocation captured: {tool_event_id}")
    
    response_event_id = hook_manager.capture_ai_response(
        "Test response", 
        "Test thinking", 
        200
    )
    print(f"  ✓ AI response captured: {response_event_id}")
    
    error_event_id = hook_manager.capture_error(
        "TestError", 
        "Test error message", 
        "Test stack trace",
        {"context": "test"}
    )
    print(f"  ✓ Error captured: {error_event_id}")
    
    # Test session stats
    stats = hook_manager.get_session_stats()
    print(f"  ✓ Events in buffer: {stats['events_in_buffer']}")
    
    # End session
    hook_manager.end_session()
    print("  ✓ Session ended")
    
    return True


def test_hook_scripts():
    """Test the hook scripts."""
    print("Testing hook scripts...")
    
    script_dir = Path(__file__).parent / "hooks"
    
    # Test user prompt hook
    cmd = [
        sys.executable, 
        str(script_dir / "user-prompt-submit-hook.py"),
        "--prompt", "Test prompt from script",
        "--verbose"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✓ User prompt hook: {result.stdout.strip()}")
    else:
        print(f"  ✗ User prompt hook failed: {result.stderr}")
        return False
    
    # Test tool use hook
    cmd = [
        sys.executable,
        str(script_dir / "tool-use-hook.py"),
        "--tool-name", "TestTool",
        "--parameters", '{"command": "test"}',
        "--response", '{"output": "test result"}',
        "--phase", "complete",
        "--success", "true",
        "--execution-time", "150",
        "--verbose"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✓ Tool use hook: {result.stdout.strip()}")
    else:
        print(f"  ✗ Tool use hook failed: {result.stderr}")
        return False
    
    # Test response hook
    cmd = [
        sys.executable,
        str(script_dir / "response-hook.py"),
        "--response", "Test AI response from script",
        "--thinking", "Test thinking process",
        "--generation-time", "300",
        "--verbose"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✓ Response hook: {result.stdout.strip()}")
    else:
        print(f"  ✗ Response hook failed: {result.stderr}")
        return False
    
    # Test error hook
    cmd = [
        sys.executable,
        str(script_dir / "error-hook.py"),
        "--error-type", "TestError",
        "--error-message", "Test error from script",
        "--recovery-action", "Test recovery",
        "--recovery-successful", "true",
        "--capture-current-stack",
        "--verbose"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✓ Error hook: {result.stdout.strip()}")
    else:
        print(f"  ✗ Error hook failed: {result.stderr}")
        return False
    
    return True


def test_sanitization():
    """Test data sanitization features."""
    print("Testing data sanitization...")
    
    hook_manager = get_hook_manager()
    hook_manager.start_session()
    
    # Test prompt with sensitive data
    sensitive_prompt = "My password is secret123 and my API key is sk-1234567890abcdef"
    event_id = hook_manager.capture_user_prompt(sensitive_prompt)
    print(f"  ✓ Sanitized prompt captured: {event_id}")
    
    # Test tool parameters with sensitive data
    sensitive_params = {
        "token": "bearer_token_12345",
        "config": {"api_key": "sk-abcdef123456", "password": "mypassword"}
    }
    event_id = hook_manager.capture_tool_invocation("TestTool", sensitive_params)
    print(f"  ✓ Sanitized tool params captured: {event_id}")
    
    hook_manager.end_session()
    return True


def test_file_operations():
    """Test file-based hook operations."""
    print("Testing file operations...")
    
    script_dir = Path(__file__).parent / "hooks"
    
    # Create temporary files for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test response from file")
        response_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is test thinking from file")
        thinking_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"test": "context", "source": "file"}, f)
        context_file = f.name
    
    try:
        # Test response hook with files
        cmd = [
            sys.executable,
            str(script_dir / "response-hook.py"),
            "--response-file", response_file,
            "--thinking-file", thinking_file,
            "--context", f'{{"context_file": "{context_file}"}}',
            "--verbose"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ File-based response hook: {result.stdout.strip()}")
        else:
            print(f"  ✗ File-based response hook failed: {result.stderr}")
            return False
        
        return True
    
    finally:
        # Cleanup temporary files
        for temp_file in [response_file, thinking_file, context_file]:
            try:
                os.unlink(temp_file)
            except:
                pass


def test_integration():
    """Test integration with ExecutionMonitor."""
    print("Testing ExecutionMonitor integration...")
    
    hook_manager = get_hook_manager()
    
    # Check that ExecutionMonitor is properly initialized
    assert hook_manager.execution_monitor is not None
    print("  ✓ ExecutionMonitor initialized")
    
    # Test session with ExecutionMonitor logging
    hook_manager.start_session()
    
    # Capture an error which should also log to ExecutionMonitor
    error_event_id = hook_manager.capture_error(
        "IntegrationTest", 
        "Testing ExecutionMonitor integration"
    )
    print(f"  ✓ Error logged to both systems: {error_event_id}")
    
    hook_manager.end_session()
    print("  ✓ Session logged to ExecutionMonitor")
    
    return True


def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(description="Test Claude Code hooks infrastructure")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    print("🧪 Testing Claude Code Hooks Infrastructure")
    print("=" * 50)
    
    tests = [
        ("Hook Manager", test_hook_manager),
        ("Hook Scripts", test_hook_scripts),
        ("Data Sanitization", test_sanitization),
        ("File Operations", test_file_operations),
        ("ExecutionMonitor Integration", test_integration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())