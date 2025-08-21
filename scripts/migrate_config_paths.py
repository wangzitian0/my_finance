#!/usr/bin/env python3
"""
Automated path migration tool for DRY principle.
Migrates all common/config references to common/config throughout the codebase.
"""

import os
import re
from pathlib import Path


def migrate_paths():
    """Migrate all common/config references to common/config"""

    # Define replacement patterns
    replacements = [
        (r"common/config", "common/config"),
        (r"data\.config", "common.config"),
        (r'"common", "config"', '"common", "config"'),
        (r"'common', 'config'", "'common', 'config'"),
    ]

    # Define file patterns to search
    file_patterns = ["**/*.py", "**/*.yml", "**/*.yaml", "**/*.md", "**/*.json"]

    # Directories to exclude
    exclude_dirs = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        "htmlcov",
        "data",  # Exclude the data submodule
    }

    root_path = Path("/Users/SP14016/zitian/my_finance")
    updated_files = []

    for pattern in file_patterns:
        for file_path in root_path.glob(pattern):
            # Skip excluded directories
            if any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # Apply all replacements
                for old_pattern, new_pattern in replacements:
                    content = re.sub(old_pattern, new_pattern, content)

                # Write back if changed
                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    updated_files.append(str(file_path))
                    print(f"✅ Updated: {file_path}")

            except (UnicodeDecodeError, PermissionError) as e:
                print(f"⚠️ Skipped {file_path}: {e}")

    print(f"\n📊 Migration complete! Updated {len(updated_files)} files.")
    return updated_files


if __name__ == "__main__":
    migrate_paths()
