#!/usr/bin/env python3
"""
Test runner for release management system.

Provides a simple way to run and validate release manager tests.
"""
import sys
import subprocess
from pathlib import Path


def run_release_manager_tests():
    """Run all release manager tests."""
    project_root = Path(__file__).parent.parent
    test_file = project_root / "tests" / "test_release_manager.py"
    
    if not test_file.exists():
        print("❌ Test file not found:", test_file)
        return False
    
    print("🧪 Running Release Manager Tests")
    print("=" * 50)
    
    # Run specific test classes
    test_classes = [
        "TestReleaseManager",
        "TestReleaseManagerIntegration", 
        "TestReleaseManagerErrorHandling"
    ]
    
    all_passed = True
    
    for test_class in test_classes:
        print(f"\n🔍 Running {test_class}")
        print("-" * 30)
        
        try:
            result = subprocess.run([
                sys.executable, str(test_file), test_class
            ], capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                print(f"✅ {test_class} - PASSED")
                # Count tests from output
                lines = result.stderr.split('\n')
                for line in lines:
                    if 'Ran' in line and 'test' in line:
                        print(f"   {line.strip()}")
            else:
                print(f"❌ {test_class} - FAILED")
                print("Error output:")
                print(result.stderr)
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error running {test_class}: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


def run_single_test(test_name: str):
    """Run a single test method."""
    project_root = Path(__file__).parent.parent
    test_file = project_root / "tests" / "test_release_manager.py"
    
    print(f"🧪 Running single test: {test_name}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, str(test_file), test_name
        ], cwd=project_root)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False


def validate_release_system():
    """Validate the release system is working correctly."""
    print("🔍 Validating Release System")
    print("=" * 50)
    
    # Import and test basic functionality
    try:
        sys.path.append(str(Path(__file__).parent.parent))
        from scripts.release_manager import ReleaseManager
        
        # Test basic instantiation
        manager = ReleaseManager()
        print("✅ ReleaseManager can be instantiated")
        
        # Test method availability
        required_methods = [
            'get_latest_build',
            'collect_release_artifacts', 
            'generate_release_manifest',
            'create_release',
            'list_releases',
            'validate_release'
        ]
        
        for method in required_methods:
            if hasattr(manager, method):
                print(f"✅ Method '{method}' available")
            else:
                print(f"❌ Method '{method}' missing")
                return False
        
        print("\n🎉 Release system validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Release system validation failed: {e}")
        return False


def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "validate":
            success = validate_release_system()
        elif command == "single" and len(sys.argv) > 2:
            test_name = sys.argv[2]
            success = run_single_test(test_name)
        elif command == "help":
            print("Release Manager Test Runner")
            print("\nUsage:")
            print("  python run_release_tests.py              # Run all tests")
            print("  python run_release_tests.py validate     # Validate system")
            print("  python run_release_tests.py single TEST  # Run single test")
            print("  python run_release_tests.py help         # Show this help")
            return
        else:
            print(f"Unknown command: {command}")
            success = False
    else:
        # Run all tests
        success = run_release_manager_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()