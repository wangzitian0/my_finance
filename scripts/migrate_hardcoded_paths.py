#!/usr/bin/env python3
"""
Hardcoded Path Migration Script
Automated refactoring tool to replace hardcoded paths with SSOT directory manager calls.

This script identifies and replaces hardcoded directory paths throughout the codebase
with calls to the unified directory manager, supporting the DRY/SSOT architecture
implementation for Issue #122.

Features:
- Pattern detection for hardcoded paths
- Safe replacement with directory manager calls
- Backup creation before changes
- Validation of replacements
- Report generation of changes made
"""

import argparse
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class PathReplacement:
    """Represents a path replacement operation"""

    file_path: str
    line_number: int
    original_pattern: str
    replacement_pattern: str
    matched_text: str
    replacement_text: str


class HardcodedPathMigrator:
    """Main migration tool for replacing hardcoded paths"""

    def __init__(self, project_root: Path, dry_run: bool = True):
        """
        Initialize migrator.

        Args:
            project_root: Root directory of the project
            dry_run: If True, don't make actual changes
        """
        self.project_root = project_root
        self.dry_run = dry_run
        self.replacements: List[PathReplacement] = []
        self.backup_dir = project_root / "backup_hardcoded_paths"

        # Define path patterns to find and replace
        self.path_patterns = self._define_path_patterns()

        # Files to exclude from migration
        self.exclude_files = {
            "migrate_hardcoded_paths.py",
            "directory_manager.py",
            "data_access.py",
            "storage_backends.py",
            "config_manager.py",
        }

        # Directories to exclude
        self.exclude_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            "backup_hardcoded_paths",
        }

    def _define_path_patterns(self) -> List[Dict[str, str]]:
        """Define patterns for hardcoded paths and their replacements"""
        return [
            # Legacy stage directories
            {
                "pattern": r'"(data/)?stage_00_original"',
                "replacement": "get_data_path(DataLayer.RAW_DATA)",
                "import_needed": "from common.directory_manager import get_data_path, DataLayer",
            },
            {
                "pattern": r'"(data/)?stage_01_extract"',
                "replacement": "get_data_path(DataLayer.DAILY_DELTA)",
                "import_needed": "from common.directory_manager import get_data_path, DataLayer",
            },
            {
                "pattern": r'"(data/)?stage_02_transform"',
                "replacement": "get_data_path(DataLayer.DAILY_INDEX)",
                "import_needed": "from common.directory_manager import get_data_path, DataLayer",
            },
            {
                "pattern": r'"(data/)?stage_03_load"',
                "replacement": "get_data_path(DataLayer.GRAPH_RAG)",
                "import_needed": "from common.directory_manager import get_data_path, DataLayer",
            },
            {
                "pattern": r'"(data/)?stage_99_build"',
                "replacement": "get_data_path(DataLayer.QUERY_RESULTS)",
                "import_needed": "from common.directory_manager import get_data_path, DataLayer",
            },
            # Build data references
            {
                "pattern": r'"build_data"',
                "replacement": "str(directory_manager.get_data_root())",
                "import_needed": "from common.directory_manager import directory_manager",
            },
            {
                "pattern": r'"data/config"',
                "replacement": "str(get_config_path())",
                "import_needed": "from common.directory_manager import get_config_path",
            },
            {
                "pattern": r'Path\("data/config"\)',
                "replacement": "get_config_path()",
                "import_needed": "from common.directory_manager import get_config_path",
            },
            # Source-specific paths
            {
                "pattern": r'"data/stage_00_original/sec-edgar"',
                "replacement": 'str(get_source_path("sec-edgar", DataLayer.RAW_DATA))',
                "import_needed": "from common.directory_manager import get_source_path, DataLayer",
            },
            {
                "pattern": r'"data/stage_00_original/yfinance"',
                "replacement": 'str(get_source_path("yfinance", DataLayer.RAW_DATA))',
                "import_needed": "from common.directory_manager import get_source_path, DataLayer",
            },
            # Build paths with timestamps
            {
                "pattern": r'"data/stage_99_build/build_(\w+)"',
                "replacement": r'str(get_build_path("\1"))',
                "import_needed": "from common.directory_manager import get_build_path",
            },
            # Path objects
            {
                "pattern": r'Path\("data"\) / "stage_00_original"',
                "replacement": "get_data_path(DataLayer.RAW_DATA)",
                "import_needed": "from common.directory_manager import get_data_path, DataLayer",
            },
            {
                "pattern": r'Path\("data"\) / "stage_99_build"',
                "replacement": "get_data_path(DataLayer.QUERY_RESULTS)",
                "import_needed": "from common.directory_manager import get_data_path, DataLayer",
            },
            # Common directory access patterns
            {
                "pattern": r'os\.path\.join\("data", "stage_00_original"\)',
                "replacement": "str(get_data_path(DataLayer.RAW_DATA))",
                "import_needed": "from common.directory_manager import get_data_path, DataLayer",
            },
        ]

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if file.endswith(".py") and file not in self.exclude_files:
                    python_files.append(Path(root) / file)

        return python_files

    def analyze_file(self, file_path: Path) -> List[PathReplacement]:
        """Analyze a file for hardcoded paths"""
        replacements = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return replacements

        for line_num, line in enumerate(lines, 1):
            for pattern_info in self.path_patterns:
                pattern = pattern_info["pattern"]
                replacement = pattern_info["replacement"]

                matches = re.finditer(pattern, line)
                for match in matches:
                    matched_text = match.group(0)

                    # Create replacement text
                    if r"\1" in replacement:  # Handle captured groups
                        replacement_text = re.sub(pattern, replacement, matched_text)
                    else:
                        replacement_text = replacement

                    replacements.append(
                        PathReplacement(
                            file_path=str(file_path),
                            line_number=line_num,
                            original_pattern=pattern,
                            replacement_pattern=replacement,
                            matched_text=matched_text,
                            replacement_text=replacement_text,
                        )
                    )

        return replacements

    def analyze_project(self) -> None:
        """Analyze entire project for hardcoded paths"""
        print("Analyzing project for hardcoded paths...")
        python_files = self.find_python_files()

        total_files = len(python_files)
        for i, file_path in enumerate(python_files, 1):
            print(f"Analyzing {i}/{total_files}: {file_path.relative_to(self.project_root)}")
            file_replacements = self.analyze_file(file_path)
            self.replacements.extend(file_replacements)

        print(f"\nFound {len(self.replacements)} hardcoded path references in {total_files} files")

    def create_backup(self) -> None:
        """Create backup of files before modification"""
        if self.dry_run:
            return

        print("Creating backup...")
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)

        # Get unique files that will be modified
        files_to_backup = set(r.file_path for r in self.replacements)

        for file_path in files_to_backup:
            src_path = Path(file_path)
            rel_path = src_path.relative_to(self.project_root)
            backup_path = self.backup_dir / rel_path

            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, backup_path)

        print(f"Backed up {len(files_to_backup)} files to {self.backup_dir}")

    def apply_replacements(self) -> None:
        """Apply all path replacements"""
        if self.dry_run:
            print("DRY RUN: Would apply the following replacements:")
            self.print_replacements_summary()
            return

        print("Applying replacements...")
        self.create_backup()

        # Group replacements by file
        files_to_modify = {}
        for replacement in self.replacements:
            file_path = replacement.file_path
            if file_path not in files_to_modify:
                files_to_modify[file_path] = []
            files_to_modify[file_path].append(replacement)

        # Apply replacements file by file
        for file_path, file_replacements in files_to_modify.items():
            self._apply_file_replacements(file_path, file_replacements)

        print(f"Applied {len(self.replacements)} replacements in {len(files_to_modify)} files")

    def _apply_file_replacements(self, file_path: str, replacements: List[PathReplacement]) -> None:
        """Apply replacements to a single file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return

        # Sort replacements by line number (descending) to avoid offset issues
        replacements.sort(key=lambda r: r.line_number, reverse=True)

        # Apply each replacement
        lines = content.split("\n")
        imports_to_add = set()

        for replacement in replacements:
            line_idx = replacement.line_number - 1
            if 0 <= line_idx < len(lines):
                old_line = lines[line_idx]
                new_line = old_line.replace(replacement.matched_text, replacement.replacement_text)
                lines[line_idx] = new_line

                # Track imports needed
                for pattern_info in self.path_patterns:
                    if pattern_info["replacement"] == replacement.replacement_pattern:
                        if "import_needed" in pattern_info:
                            imports_to_add.add(pattern_info["import_needed"])

        # Add needed imports at the top
        if imports_to_add:
            lines = self._add_imports(lines, imports_to_add)

        # Write back to file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception as e:
            print(f"Error writing {file_path}: {e}")

    def _add_imports(self, lines: List[str], imports_to_add: Set[str]) -> List[str]:
        """Add import statements to the top of the file"""
        # Find where to insert imports (after existing imports)
        insert_idx = 0
        in_docstring = False
        docstring_chars = ['"""', "'''"]

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip shebang and encoding declarations
            if stripped.startswith("#"):
                insert_idx = i + 1
                continue

            # Handle docstrings
            for quote in docstring_chars:
                if quote in stripped:
                    if not in_docstring:
                        in_docstring = True
                        if stripped.count(quote) >= 2:  # Single line docstring
                            in_docstring = False
                    else:
                        in_docstring = False
                    break

            if in_docstring:
                insert_idx = i + 1
                continue

            # Find last import statement
            if stripped.startswith(("import ", "from ")) and not in_docstring:
                insert_idx = i + 1
            elif stripped and not in_docstring:
                break

        # Insert new imports
        new_lines = lines[:insert_idx]
        for import_stmt in sorted(imports_to_add):
            # Check if import already exists
            if not any(import_stmt in line for line in lines[:insert_idx]):
                new_lines.append(import_stmt)

        if imports_to_add:
            new_lines.append("")  # Add blank line after imports

        new_lines.extend(lines[insert_idx:])
        return new_lines

    def print_replacements_summary(self) -> None:
        """Print summary of all replacements"""
        if not self.replacements:
            print("No hardcoded paths found.")
            return

        # Group by file
        files_summary = {}
        for replacement in self.replacements:
            file_path = replacement.file_path
            if file_path not in files_summary:
                files_summary[file_path] = []
            files_summary[file_path].append(replacement)

        print(f"\nFound {len(self.replacements)} hardcoded path references:")
        print("=" * 60)

        for file_path, file_replacements in files_summary.items():
            rel_path = Path(file_path).relative_to(self.project_root)
            print(f"\n📁 {rel_path} ({len(file_replacements)} replacements)")

            for replacement in file_replacements:
                print(f"  Line {replacement.line_number}:")
                print(f"    - {replacement.matched_text}")
                print(f"    + {replacement.replacement_text}")

    def generate_report(self, output_file: Path) -> None:
        """Generate detailed migration report"""
        report_content = []
        report_content.append("# Hardcoded Path Migration Report")
        report_content.append(f"Generated: {os.popen('date').read().strip()}")
        report_content.append(f"Project: {self.project_root}")
        report_content.append(f"Mode: {'DRY RUN' if self.dry_run else 'APPLIED'}")
        report_content.append(f"Total replacements: {len(self.replacements)}")
        report_content.append("")

        # Group by file
        files_summary = {}
        for replacement in self.replacements:
            file_path = replacement.file_path
            if file_path not in files_summary:
                files_summary[file_path] = []
            files_summary[file_path].append(replacement)

        for file_path, file_replacements in files_summary.items():
            rel_path = Path(file_path).relative_to(self.project_root)
            report_content.append(f"## {rel_path}")
            report_content.append(f"Replacements: {len(file_replacements)}")
            report_content.append("")

            for replacement in file_replacements:
                report_content.append(f"**Line {replacement.line_number}:**")
                report_content.append(f"```python")
                report_content.append(f"# Before:")
                report_content.append(f"{replacement.matched_text}")
                report_content.append(f"# After:")
                report_content.append(f"{replacement.replacement_text}")
                report_content.append(f"```")
                report_content.append("")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(report_content))

        print(f"Report generated: {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Migrate hardcoded paths to SSOT directory manager"
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--report", type=Path, help="Generate report file")

    args = parser.parse_args()

    project_root = args.project_root or Path.cwd()
    if not project_root.exists():
        print(f"Error: Project root not found: {project_root}")
        sys.exit(1)

    # Initialize migrator
    migrator = HardcodedPathMigrator(project_root, dry_run=not args.apply)

    # Analyze project
    migrator.analyze_project()

    if not migrator.replacements:
        print("No hardcoded paths found. Migration not needed.")
        return

    # Apply or preview replacements
    migrator.apply_replacements()

    # Generate report if requested
    if args.report:
        migrator.generate_report(args.report)
    elif not args.report and not args.apply:
        # Generate default report for dry runs
        report_file = project_root / "hardcoded_paths_migration_report.md"
        migrator.generate_report(report_file)


if __name__ == "__main__":
    main()
