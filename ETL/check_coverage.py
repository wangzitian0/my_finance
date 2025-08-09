#!/usr/bin/env python3
"""
Coverage threshold checker for test pipeline
"""
import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def check_coverage_threshold(threshold: int = 80) -> bool:
    """
    Check if test coverage meets the threshold

    Args:
        threshold: Minimum coverage percentage required

    Returns:
        bool: True if coverage meets threshold, False otherwise
    """
    coverage_file = Path("coverage.xml")

    if not coverage_file.exists():
        print("❌ Coverage file not found. Run tests with coverage first.")
        return False

    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()

        # Extract overall coverage percentage
        coverage_attr = root.attrib.get("line-rate")
        if coverage_attr:
            coverage_percent = float(coverage_attr) * 100
        else:
            print("❌ Could not parse coverage percentage from XML")
            return False

        print(f"📊 Current test coverage: {coverage_percent:.1f}%")
        print(f"🎯 Required threshold: {threshold}%")

        if coverage_percent >= threshold:
            print(
                f"✅ Coverage meets threshold ({coverage_percent:.1f}% >= {threshold}%)"
            )
            return True
        else:
            print(
                f"❌ Coverage below threshold ({coverage_percent:.1f}% < {threshold}%)"
            )

            # Show detailed breakdown for improvement
            show_coverage_breakdown(root)
            return False

    except Exception as e:
        print(f"❌ Error parsing coverage file: {e}")
        return False


def show_coverage_breakdown(root):
    """Show detailed coverage breakdown by module"""
    print("\n📋 Coverage breakdown by module:")
    print("-" * 50)

    packages = root.findall(".//package")
    for package in packages:
        package_name = package.get("name", "Unknown")
        line_rate = float(package.get("line-rate", 0)) * 100

        if line_rate < 80:  # Show modules that need improvement
            print(f"⚠️  {package_name}: {line_rate:.1f}%")
        else:
            print(f"✅ {package_name}: {line_rate:.1f}%")


def main():
    parser = argparse.ArgumentParser(description="Check test coverage threshold")
    parser.add_argument(
        "--threshold",
        type=int,
        default=80,
        help="Minimum coverage threshold (default: 80)",
    )

    args = parser.parse_args()

    success = check_coverage_threshold(args.threshold)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
