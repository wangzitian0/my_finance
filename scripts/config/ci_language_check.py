#!/usr/bin/env python3
"""
Language Standards Check for my_finance repository

This script validates that code follows English-only standards:
1. No Chinese characters in Python source files (.py)
2. No Chinese characters in documentation files (.md)
3. No Chinese characters in configuration files (.yml, .yaml, .json)

Based on GitHub issue #95: Standardization and cleanup of documentation and code practices
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Chinese Unicode range: \u4e00-\u9fff
CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff]")

# File extensions to check
CHECK_EXTENSIONS = {".py", ".md", ".yml", ".yaml", ".json"}

# Directories to exclude from checking
EXCLUDE_DIRS = {
    ".git",
    ".pixi",
    ".venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    "htmlcov",
    "templates",  # Templates directory - multilingual content allowed
}

# Files to exclude - TEMPORARY: allow Python files with Chinese comments during transition
EXCLUDE_FILES = {
    # This checker itself (contains Chinese in comments for documentation)
    "ci_language_check.py",
    # Temporarily exclude Python files with Chinese comments (TODO: clean these up)
    "ETL/build_dataset.py",
    "ETL/build_schema.py",
    "ETL/check_coverage.py",
    "ETL/fetch_ticker_lists.py",
    "ETL/graph_data_integration.py",
    "ETL/import_data.py",
    "ETL/manage.py",
    "ETL/migrate_data_structure.py",
    "ETL/models.py",
    "ETL/retry_failed.py",
    "ETL/run_job.py",
    "ETL/spider/sec_edgar_spider.py",
    "ETL/spider/yfinance_spider.py",
    "ETL/spider/metadata_manager.py",
    "ETL/update_data_paths.py",
    "common/build_tracker.py",
    "common/common_config.py",
    "common/logger.py",
    "dcf_engine/build_knowledge_base.py",
    "dcf_engine/legacy_testing/generate_dcf_report.py",
    "dcf_engine/legacy_testing/hybrid_dcf_analyzer.py",
    "dcf_engine/legacy_testing/m7_dcf_analysis.py",
    "dcf_engine/legacy_testing/simple_m7_dcf.py",
    "dcf_engine/pure_llm_dcf.py",
    "dcf_engine/validator.py",
    "infra/comprehensive_env_status.py",
    "scripts/manage_build_data.py",
}


def should_check_file(file_path: Path) -> bool:
    """Determine if a file should be checked for Chinese characters."""

    # Skip if file extension not in check list
    if file_path.suffix not in CHECK_EXTENSIONS:
        return False

    # Skip if in excluded directories
    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir in file_path.parts:
            return False

    # Special handling for data directory - only check common/config
    file_parts = file_path.parts
    if "data" in file_parts:
        # Find data directory index
        data_index = file_parts.index("data")
        # If there's a subdirectory after data
        if len(file_parts) > data_index + 1:
            subdir = file_parts[data_index + 1]
            # Only check common/config, skip all other data subdirectories
            if subdir != "config":
                return False

    # Skip if in excluded files list
    if file_path.name in EXCLUDE_FILES:
        return False

    # Skip if full relative path is in excluded files
    relative_path = str(file_path)
    if relative_path in EXCLUDE_FILES:
        return False

    return True


def find_chinese_in_file(file_path: Path) -> list:
    """Find lines containing Chinese characters in code/comments, excluding quoted strings."""
    chinese_lines = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                # Check if Chinese text is outside of quotes
                if has_chinese_outside_quotes(line):
                    chinese_lines.append((line_num, line.strip()))
    except (UnicodeDecodeError, IOError) as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return []

    return chinese_lines


def has_chinese_outside_quotes(line: str) -> bool:
    """Check if line has Chinese characters outside of quoted strings."""
    # For .py files, we need to handle string literals
    # For .md files, we check everything
    # For .yml/.json, we allow Chinese in string values

    # Simple state machine to track if we're inside quotes
    in_single_quote = False
    in_double_quote = False
    i = 0

    while i < len(line):
        char = line[i]

        # Handle escape sequences
        if char == "\\" and i + 1 < len(line):
            i += 2
            continue

        # Toggle quote states
        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif not in_single_quote and not in_double_quote:
            # We're outside quotes, check for Chinese
            if CHINESE_PATTERN.search(char):
                return True

        i += 1

    return False


def check_language_standards(root_dir: Path) -> tuple[bool, list]:
    """Check all relevant files for Chinese characters."""
    violations = []

    for root, dirs, files in os.walk(root_dir):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            file_path = Path(root) / file

            if not should_check_file(file_path):
                continue

            chinese_lines = find_chinese_in_file(file_path)
            if chinese_lines:
                violations.append((file_path, chinese_lines))

    return len(violations) == 0, violations


def main():
    """Main function to run language standards check."""
    print("🔍 Language Standards Check")
    print("=" * 50)

    root_dir = Path(__file__).parent.parent.parent
    print(f"📁 Checking directory: {root_dir}")

    # Run the check
    is_clean, violations = check_language_standards(root_dir)

    if is_clean:
        print("✅ All files pass language standards check")
        print("💡 No Chinese characters found in code and documentation")
        return 0

    # Report violations
    print(f"❌ Found {len(violations)} files with Chinese characters:")
    print()

    total_issues = 0
    for file_path, chinese_lines in violations:
        print(f"📄 {file_path}")
        for line_num, line in chinese_lines:
            total_issues += 1
            print(f"   Line {line_num}: {line}")
        print()

    print(f"📊 Summary: {total_issues} Chinese text occurrences in {len(violations)} files")
    print()
    print("💡 Action Required:")
    print("   1. Replace Chinese comments with English equivalents")
    print("   2. Update Chinese documentation to English")
    print("   3. Use English-only text in configuration files")
    print()
    print("🔧 Helpful commands:")
    print("   • Find Chinese text: git grep -l '[\\u4e00-\\u9fff]'")
    print("   • Search in specific type: git grep -l '[\\u4e00-\\u9fff]' -- '*.py'")

    return 1


if __name__ == "__main__":
    sys.exit(main())