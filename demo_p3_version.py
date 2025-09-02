#!/usr/bin/env python3
"""
P3 Version Management System Demo

This script demonstrates all the features of the P3 version management system.
Run this to see the complete functionality in action.
"""

import os
import sys
from pathlib import Path

def demo_basic_version_info():
    """Demo basic version information display."""
    print("🔧 P3 Version Management System Demo")
    print("=" * 50)
    print("\n📋 1. Basic Version Information")
    print("-" * 30)
    
    try:
        from p3_version import print_version_info
        print_version_info()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_version_string():
    """Demo version string generation."""
    print("\n📋 2. Version String Generation")
    print("-" * 30)
    
    try:
        from p3_version import get_p3_version, get_version_manager
        
        version_string = get_p3_version()
        print(f"Simple version string: {version_string}")
        
        manager = get_version_manager()
        detailed_info = manager.get_version_info()
        
        print(f"Detailed version: {detailed_info['version_string']}")
        print(f"Build number: {detailed_info.get('build', 0)}")
        print(f"Update count: {detailed_info.get('update_count', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_update_check():
    """Demo version update checking."""
    print("\n📋 3. Version Update Check")
    print("-" * 30)
    
    try:
        from p3_version import print_update_check
        print_update_check()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_version_history():
    """Demo version history display."""
    print("\n📋 4. Version History")
    print("-" * 30)
    
    try:
        from p3_version import print_version_history
        print_version_history()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_manual_version_operations():
    """Demo manual version operations (without actually changing version)."""
    print("\n📋 5. Manual Version Operations")
    print("-" * 30)
    
    try:
        from p3_version import get_version_manager
        manager = get_version_manager()
        
        current_version = manager.get_version_string()
        print(f"Current version: {current_version}")
        
        # Show what each increment would result in (without actually doing it)
        data = manager._load_version_data()
        
        print(f"Available increment levels:")
        print(f"  • major: would result in {data['major']+1}.0.0")
        print(f"  • minor: would result in {data['major']}.{data['minor']+1}.0")
        print(f"  • patch: would result in {data['major']}.{data['minor']}.{data['patch']+1}")
        print(f"  • build: would result in {data['major']}.{data['minor']}.{data['patch']}.{data['build']+1}")
        
        print(f"\n💡 Use 'p3 version-increment [level]' to actually increment version")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_git_integration():
    """Demo git integration features."""
    print("\n📋 6. Git Integration")
    print("-" * 30)
    
    try:
        from p3_version import get_version_manager
        manager = get_version_manager()
        
        git_hash = manager._get_git_hash()
        git_branch = manager._get_git_branch()
        git_dir = manager._get_git_dir()
        is_dirty = manager._is_git_dirty()
        commits_ahead = manager._get_commits_since_last_update()
        
        print(f"Git Hash: {git_hash}")
        print(f"Git Branch: {git_branch}")
        print(f"Git Directory: {git_dir}")
        print(f"Working Directory Clean: {'No' if is_dirty else 'Yes'}")
        print(f"Commits Since Last Update: {commits_ahead}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_hook_installation_status():
    """Demo git hooks installation status."""
    print("\n📋 7. Git Hooks Installation Status")
    print("-" * 30)
    
    try:
        from p3_version import get_version_manager
        manager = get_version_manager()
        
        git_dir = manager._get_git_dir()
        if git_dir:
            hooks_dir = git_dir / "hooks"
            post_merge_hook = hooks_dir / "post-merge"
            
            print(f"Git hooks directory: {hooks_dir}")
            print(f"Post-merge hook exists: {post_merge_hook.exists()}")
            
            if post_merge_hook.exists():
                try:
                    with open(post_merge_hook, 'r') as f:
                        content = f.read()
                    has_p3_logic = "p3_version.py" in content
                    print(f"Contains P3 version logic: {has_p3_logic}")
                    if has_p3_logic:
                        print("✅ Automatic version updates enabled after git pull")
                    else:
                        print("⚠️  Hook exists but may not update P3 version")
                except Exception:
                    print("⚠️  Could not read hook file")
            else:
                print("⚠️  Run 'p3 install-version-hooks' to enable automatic updates")
        else:
            print("❌ Could not detect git directory")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_p3_cli_integration():
    """Demo P3 CLI integration."""
    print("\n📋 8. P3 CLI Integration")
    print("-" * 30)
    
    try:
        # Import p3 module
        sys.path.insert(0, str(Path(__file__).parent))
        import p3
        
        # Check version availability
        version_enabled = getattr(p3, 'VERSION_ENABLED', False)
        print(f"Version management enabled in P3: {version_enabled}")
        
        # List version commands
        cli = p3.P3CLI()
        version_commands = [cmd for cmd in cli.commands.keys() if cmd.startswith('version')]
        print(f"Available version commands: {', '.join(version_commands)}")
        
        # Show command mappings
        print(f"\nVersion command mappings:")
        for cmd in version_commands:
            if cmd in cli.commands:
                print(f"  p3 {cmd} -> {cli.commands[cmd]}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_all_commands():
    """Show examples of all available P3 version commands."""
    print("\n📋 9. Available P3 Commands")
    print("-" * 30)
    
    commands = [
        ("p3 version", "Show current P3 version and git information"),
        ("p3 version-info", "Same as version command (detailed info)"),
        ("p3 version-increment [level]", "Manually increment version (major|minor|patch|build)"),
        ("p3 version-update", "Update version after git pull (auto-detects changes)"),
        ("p3 version-check", "Check for potential version updates needed"),
        ("p3 version-history", "Show version change history and git commits"),
        ("p3 install-version-hooks", "Install git hooks for automatic version updates"),
    ]
    
    print("Available P3 version management commands:")
    for cmd, desc in commands:
        print(f"  {cmd:<30} - {desc}")
    
    print(f"\n💡 All commands are integrated into the P3 CLI system")
    
    return True

def run_full_demo():
    """Run the complete P3 version management demo."""
    print("🚀 Starting P3 Version Management System Demo")
    
    demos = [
        ("Basic Version Information", demo_basic_version_info),
        ("Version String Generation", demo_version_string),
        ("Update Check", demo_update_check),
        ("Version History", demo_version_history),
        ("Manual Version Operations", demo_manual_version_operations),
        ("Git Integration", demo_git_integration),
        ("Hook Installation Status", demo_hook_installation_status),
        ("P3 CLI Integration", demo_p3_cli_integration),
        ("Available Commands", demo_all_commands),
    ]
    
    results = []
    for demo_name, demo_func in demos:
        try:
            success = demo_func()
            results.append((demo_name, success))
        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Demo '{demo_name}' failed with error: {e}")
            results.append((demo_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Demo Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for demo_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {demo_name}")
    
    print(f"\nResult: {passed}/{total} demos completed successfully")
    
    if passed == total:
        print("\n🎉 P3 Version Management System is fully functional!")
        print("\n🚀 Quick Start Guide:")
        print("1. Run 'p3 version' to see current version")
        print("2. Run 'p3 install-version-hooks' to enable automatic updates")
        print("3. After git pull, version will auto-increment")
        print("4. Use 'p3 version-increment [level]' for manual updates")
        print("5. Use 'p3 version-check' to check if update is needed")
    else:
        print(f"\n⚠️  Some features may not be working correctly.")
    
    return passed == total

if __name__ == "__main__":
    success = run_full_demo()
    print(f"\n{'='*60}")
    print("✨ P3 Version Management Demo Complete!")
    print("=" * 60)
    sys.exit(0 if success else 1)