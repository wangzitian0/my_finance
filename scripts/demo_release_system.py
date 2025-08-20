#!/usr/bin/env python3
"""
Demo script for the Release Management System

Demonstrates key features and usage of the my_finance release management system.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.release_manager import ReleaseManager


def demo_release_system():
    """Demonstrate the release management system capabilities."""
    print("🚀 My Finance Release Management System Demo")
    print("=" * 60)

    # Initialize release manager
    print("\n1. Initializing Release Manager...")
    manager = ReleaseManager()
    print("✅ Release Manager initialized")

    # Check for latest build
    print("\n2. Finding Latest Build...")
    latest_build = manager.get_latest_build()
    if latest_build:
        print(f"✅ Found latest build: {latest_build.name}")
        print(f"   Path: {latest_build}")
    else:
        print("❌ No builds found")
        print("   Run 'p3 fast-build m7' to create a build first")
        return False

    # Collect artifacts
    print("\n3. Collecting Release Artifacts...")
    artifacts = manager.collect_release_artifacts(latest_build)
    total_files = sum(len(files) for files in artifacts.values())
    print(f"✅ Collected {total_files} artifacts")

    for category, files in artifacts.items():
        if files:
            print(f"   - {category}: {len(files)} files")

    # Generate manifest
    print("\n4. Generating Release Manifest...")
    manifest = manager.generate_release_manifest(artifacts, "demo_release", latest_build)
    print("✅ Manifest generated")
    print(f"   Total files: {manifest['statistics']['total_files']}")
    print(f"   Total size: {manifest['statistics']['total_size']:,} bytes")

    # List existing releases
    print("\n5. Listing Existing Releases...")
    releases = manager.list_releases()
    if releases:
        print(f"✅ Found {len(releases)} existing releases:")
        for release in releases[:5]:  # Show first 5
            print(f"   - {release}")
        if len(releases) > 5:
            print(f"   ... and {len(releases) - 5} more")
    else:
        print("ℹ️  No existing releases found")

    # Create a demo release (with user confirmation)
    print("\n6. Creating Demo Release...")
    try:
        print("   Creating 'system_demo_release'...")
        release_id, manifest = manager.create_release("system_demo_release")
        print(f"✅ Release created successfully: {release_id}")
        print(f"   Files: {manifest['statistics']['total_files']}")
        print(f"   Size: {manifest['statistics']['total_size']:,} bytes")

        # Validate the release
        print("\n7. Validating Release...")
        is_valid = manager.validate_release(release_id)
        if is_valid:
            print("✅ Release validation passed")
        else:
            print("❌ Release validation failed")

    except Exception as e:
        print(f"❌ Error creating release: {e}")
        return False

    # Final summary
    print("\n" + "=" * 60)
    print("🎉 Release Management System Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("✅ Build detection and artifact collection")
    print("✅ Manifest generation with metadata")
    print("✅ Release creation and packaging")
    print("✅ Release listing and validation")
    print("✅ Comprehensive error handling")

    print(f"\nDemo release created: {release_id}")
    print("Run 'python scripts/release_manager.py list' to see all releases")
    print("Run 'python scripts/release_manager.py validate --release-id RELEASE_ID' to validate")

    return True


def show_release_commands():
    """Show available release management commands."""
    print("🛠️  Available Release Management Commands")
    print("=" * 50)

    commands = [
        ("Create Release", "python scripts/release_manager.py create --name 'my_release'"),
        ("List Releases", "python scripts/release_manager.py list"),
        (
            "Validate Release",
            "python scripts/release_manager.py validate --release-id 'release_id'",
        ),
        ("", ""),
        ("Via p3 (when integrated)", ""),
        ("Create Release", "p3 create-release --name 'my_release'"),
        ("List Releases", "p3 list-releases"),
        ("Validate Release", "p3 validate-release 'release_id'"),
    ]

    for description, command in commands:
        if description and command:
            print(f"{description:20} {command}")
        elif description:
            print(f"\n{description}")
        else:
            print()


def check_system_requirements():
    """Check if system meets requirements for release management."""
    print("🔍 Checking System Requirements")
    print("=" * 40)

    requirements = []

    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor} (>=3.8 required)")
        requirements.append(True)
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} (>=3.8 required)")
        requirements.append(False)

    # Check required modules
    required_modules = ["json", "pathlib", "datetime", "shutil", "subprocess"]
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ Module '{module}' available")
            requirements.append(True)
        except ImportError:
            print(f"❌ Module '{module}' missing")
            requirements.append(False)

    # Check project structure
    project_root = Path(__file__).parent.parent
    required_dirs = ["data", "scripts", "tests"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ Directory '{dir_name}' exists")
            requirements.append(True)
        else:
            print(f"❌ Directory '{dir_name}' missing")
            requirements.append(False)

    all_ok = all(requirements)
    print("\n" + "=" * 40)
    if all_ok:
        print("🎉 All requirements met!")
    else:
        print("❌ Some requirements not met")

    return all_ok


def main():
    """Main demo function."""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "check":
            success = check_system_requirements()
        elif command == "commands":
            show_release_commands()
            success = True
        elif command == "help":
            print("Release Management System Demo")
            print("\nUsage:")
            print("  python demo_release_system.py           # Run full demo")
            print("  python demo_release_system.py check     # Check requirements")
            print("  python demo_release_system.py commands  # Show commands")
            print("  python demo_release_system.py help      # Show this help")
            success = True
        else:
            print(f"Unknown command: {command}")
            success = False
    else:
        # Run full demo
        success = demo_release_system()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
