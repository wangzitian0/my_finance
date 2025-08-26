#!/usr/bin/env python3
import subprocess
import sys
import os

def run_command(cmd, description):
    print(f'🔄 {description}...')
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print(f'Command: {cmd}')
    print(f'Return code: {result.returncode}')
    print(f'Stdout: {repr(result.stdout)}')
    print(f'Stderr: {repr(result.stderr)}')
    
    if result.returncode == 0:
        print(f'✅ {description} - SUCCESS')
        return result.stdout.strip()
    else:
        print(f'❌ {description} - FAILED')
        return None

def get_current_branch():
    """Get current git branch"""
    result = run_command("git branch --show-current", "Getting current branch")
    return result

print("=== Branch Detection Debug ===")
print(f"Working directory: {os.getcwd()}")
print(f"Git dir: {os.path.exists('.git')}")

# Test different ways to get branch
branch1 = get_current_branch()
print(f"Method 1 result: '{branch1}'")

result2 = run_command("git rev-parse --abbrev-ref HEAD", "Getting branch via rev-parse")
print(f"Method 2 result: '{result2}'")

result3 = run_command("git symbolic-ref --short HEAD", "Getting branch via symbolic-ref")
print(f"Method 3 result: '{result3}'")

# Test git status
run_command("git status --porcelain", "Git status check")