#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Structure Validation Utilities

Provides utilities for validating and maintaining consistent module structure
across the entire project. Ensures proper Python package organization and
import path consistency.

Issue #256: Directory structure adjustment Phase 2
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


def validate_init_file(init_path: Path) -> Dict[str, bool]:
    """
    Validate an __init__.py file for proper structure.

    Args:
        init_path: Path to the __init__.py file

    Returns:
        Dictionary with validation results
    """
    results = {
        "exists": False,
        "has_shebang": False,
        "has_encoding": False,
        "has_docstring": False,
        "has_all_definition": False,
        "has_proper_imports": False,
    }

    if not init_path.exists():
        return results

    results["exists"] = True

    try:
        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()

        # Check for shebang
        if lines and lines[0].startswith("#!/usr/bin/env python3"):
            results["has_shebang"] = True

        # Check for encoding declaration
        for line in lines[:3]:  # Check first 3 lines
            if "utf-8" in line and ("coding" in line or "encoding" in line):
                results["has_encoding"] = True
                break

        # Parse AST to check for docstring and __all__
        try:
            tree = ast.parse(content)

            # Check for module docstring
            if (
                tree.body
                and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str)
            ):
                results["has_docstring"] = True

            # Check for __all__ definition
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign) and any(
                    isinstance(target, ast.Name) and target.id == "__all__"
                    for target in node.targets
                ):
                    results["has_all_definition"] = True
                    break

            # Check for proper import structure
            has_imports = any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in tree.body)
            if has_imports:
                results["has_proper_imports"] = True

        except SyntaxError:
            logger.warning(f"Syntax error in {init_path}")

    except Exception as e:
        logger.error(f"Error validating {init_path}: {e}")

    return results


def find_python_packages(root_path: Path) -> List[Path]:
    """
    Find all Python packages (directories with __init__.py files).

    Args:
        root_path: Root directory to search from

    Returns:
        List of package directory paths
    """
    packages = []

    # Skip these directories
    skip_dirs = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".pixi",
        "build_data",
        ".venv",
        "venv",
        "node_modules",
        ".mypy_cache",
        ".coverage",
    }

    for path in root_path.rglob("*"):
        if (
            path.is_dir()
            and path.name not in skip_dirs
            and not any(part.startswith(".") for part in path.parts[len(root_path.parts) :])
            and (path / "__init__.py").exists()
        ):
            packages.append(path)

    return sorted(packages)


def validate_module_structure(root_path: Optional[Path] = None) -> Dict[str, any]:
    """
    Validate the entire module structure of the project.

    Args:
        root_path: Root directory to validate (defaults to current directory)

    Returns:
        Dictionary with comprehensive validation results
    """
    if root_path is None:
        root_path = Path.cwd()

    packages = find_python_packages(root_path)

    results = {
        "total_packages": len(packages),
        "l1_packages": [],
        "l2_packages": [],
        "l3_plus_packages": [],
        "validation_summary": {"passed": 0, "failed": 0, "warnings": 0},
        "detailed_results": {},
    }

    for package_path in packages:
        relative_path = package_path.relative_to(root_path)
        level = len(relative_path.parts)

        # Categorize by depth
        if level == 1:
            results["l1_packages"].append(str(relative_path))
        elif level == 2:
            results["l2_packages"].append(str(relative_path))
        else:
            results["l3_plus_packages"].append(str(relative_path))

        # Validate the __init__.py file
        init_path = package_path / "__init__.py"
        validation = validate_init_file(init_path)

        results["detailed_results"][str(relative_path)] = validation

        # Count results
        required_checks = ["exists", "has_docstring"]
        passed_required = all(validation[check] for check in required_checks)

        if passed_required:
            results["validation_summary"]["passed"] += 1
        else:
            results["validation_summary"]["failed"] += 1

        # Check for warnings
        recommended_checks = ["has_shebang", "has_encoding", "has_all_definition"]
        if passed_required and not all(validation[check] for check in recommended_checks):
            results["validation_summary"]["warnings"] += 1

    return results


def generate_validation_report(results: Dict[str, any]) -> str:
    """
    Generate a human-readable validation report.

    Args:
        results: Results from validate_module_structure()

    Returns:
        Formatted report string
    """
    report = []
    report.append("Module Structure Validation Report")
    report.append("=" * 50)

    # Summary
    total = results["total_packages"]
    summary = results["validation_summary"]
    report.append(f"Total packages found: {total}")
    report.append(f"L1 packages: {len(results['l1_packages'])}")
    report.append(f"L2 packages: {len(results['l2_packages'])}")
    report.append(f"L3+ packages: {len(results['l3_plus_packages'])}")
    report.append("")

    # Validation summary
    report.append(f"Validation Results:")
    report.append(f"  ✅ Passed: {summary['passed']}")
    report.append(f"  ❌ Failed: {summary['failed']}")
    report.append(f"  ⚠️ Warnings: {summary['warnings']}")
    report.append("")

    # Failed packages
    if summary["failed"] > 0:
        report.append("Failed Packages:")
        for package, validation in results["detailed_results"].items():
            if not validation["exists"] or not validation["has_docstring"]:
                report.append(f"  ❌ {package}")
                if not validation["exists"]:
                    report.append(f"      - Missing __init__.py file")
                if not validation["has_docstring"]:
                    report.append(f"      - Missing module docstring")
        report.append("")

    # Warnings
    if summary["warnings"] > 0:
        report.append("Packages with Warnings:")
        for package, validation in results["detailed_results"].items():
            required_passed = validation["exists"] and validation["has_docstring"]
            if required_passed:
                warnings = []
                if not validation["has_shebang"]:
                    warnings.append("Missing shebang")
                if not validation["has_encoding"]:
                    warnings.append("Missing encoding declaration")
                if not validation["has_all_definition"]:
                    warnings.append("Missing __all__ definition")

                if warnings:
                    report.append(f"  ⚠️ {package}")
                    for warning in warnings:
                        report.append(f"      - {warning}")
        report.append("")

    return "\n".join(report)


if __name__ == "__main__":
    # Run validation when executed directly
    results = validate_module_structure()
    report = generate_validation_report(results)
    print(report)
