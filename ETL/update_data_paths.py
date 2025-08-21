#!/usr/bin/env python3
"""
Script to update data paths from 'data/original' to new ETL stage structure.
Updates all relevant Python files to use the new directory structure.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def update_file_paths(file_path: str, replacements: List[Tuple[str, str]]) -> bool:
    """Update file paths in a given file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        for old_pattern, new_pattern in replacements:
            content = re.sub(old_pattern, new_pattern, content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True

        return False

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def main():
    """Main function to update all files"""
    base_dir = Path("/Users/SP14016/zitian/my_finance")

    # Define path replacement patterns
    replacements = [
        # Direct path replacements
        (r"data/stage_01_extract/yfinance", "data/stage_01_extract/yfinance"),
        (r"data/stage_01_extract/sec_edgar", "data/stage_01_extract/sec_edgar"),
        (r"data\\\\original\\\\yfinance", "data/stage_01_extract/yfinance"),
        (r"data\\\\original\\\\sec-edgar", "data/stage_01_extract/sec_edgar"),
        # Python os.path.join patterns
        (r'"data", "stage_01_extract", "yfinance"', '"data", "stage_01_extract", "yfinance"'),
        (r'"data", "stage_01_extract", "sec_edgar"', '"data", "stage_01_extract", "sec_edgar"'),
        (r"'data', 'stage_01_extract', 'yfinance'", "'data', 'stage_01_extract', 'yfinance'"),
        (r"'data', 'stage_01_extract', 'sec_edgar'", "'data', 'stage_01_extract', 'sec_edgar'"),
        # Path concatenation patterns
        (r'data" \+ "/original"', 'data" + "/stage_01_extract"'),
        (r"data' \+ '/original'", "data' + '/stage_01_extract'"),
        # Configuration and documentation references
        (r"stage_01_extract/yfinance", "stage_01_extract/yfinance"),
        (r"stage_01_extract/sec_edgar", "stage_01_extract/sec_edgar"),
        (r"stage_01_extract/sec_edgar", "stage_01_extract/sec_edgar"),
    ]

    # Files to update (excluding migration files and backups)
    files_to_update = []

    # Find all Python files
    for pattern in ["*.py", "**/*.py"]:
        for file_path in base_dir.glob(pattern):
            # Skip backup, migration, and git files
            if any(
                exclude in str(file_path)
                for exclude in [
                    "backup/",
                    ".git/",
                    "migrate_data_structure.py",
                    "__pycache__/",
                    ".pixi/",
                    "htmlcov/",
                ]
            ):
                continue
            files_to_update.append(str(file_path))

    # Find markdown and YAML files in docs and config
    for pattern in ["docs/*.md", "common/config/*.yml", "*.md"]:
        for file_path in base_dir.glob(pattern):
            if ".git/" not in str(file_path):
                files_to_update.append(str(file_path))

    print(f"Found {len(files_to_update)} files to update")

    updated_files = 0
    for file_path in files_to_update:
        if update_file_paths(file_path, replacements):
            updated_files += 1

    print(f"Updated {updated_files} files")

    # Special handling for common/metadata_manager.py if it needs ticker-based logic
    metadata_manager_path = base_dir / "common" / "metadata_manager.py"
    if metadata_manager_path.exists():
        print(f"\nNote: You may need to manually review {metadata_manager_path}")
        print("to ensure it handles the new date-partitioned directory structure correctly.")

    # Special handling for ETL/import_data.py
    etl_import_path = base_dir / "ETL" / "import_data.py"
    if etl_import_path.exists():
        print(f"\nNote: You may need to manually review {etl_import_path}")
        print("to ensure it reads from the new stage_01_extract structure correctly.")


if __name__ == "__main__":
    main()
