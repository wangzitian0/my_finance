#!/usr/bin/env python3
"""
Fix path handling inconsistencies across the codebase
Standardize on pathlib.Path instead of os.path for better cross-platform compatibility
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class PathFixture:
    """Fix path handling inconsistencies in Python files"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.patterns = {
            # os.path.join patterns
            r"os\.path\.join\s*\(\s*([^)]+)\s*\)": self._fix_os_path_join,
            r"os\.path\.abspath\s*\(\s*([^)]+)\s*\)": self._fix_os_path_abspath,
            r"os\.path\.dirname\s*\(\s*([^)]+)\s*\)": self._fix_os_path_dirname,
            r"os\.path\.basename\s*\(\s*([^)]+)\s*\)": self._fix_os_path_basename,
            r"os\.path\.exists\s*\(\s*([^)]+)\s*\)": self._fix_os_path_exists,
            r"os\.path\.isdir\s*\(\s*([^)]+)\s*\)": self._fix_os_path_isdir,
            r"os\.path\.isfile\s*\(\s*([^)]+)\s*\)": self._fix_os_path_isfile,
            # Relative path patterns
            r'["\']\.\./[^"\']*["\']': self._fix_relative_paths,
            r'["\']\./[^"\']*["\']': self._fix_current_dir_paths,
        }

        self.files_to_fix = [
            "ETL/import_data.py",
            "common/metadata_manager.py",
            "dcf_engine/build_knowledge_base.py",
        ]

    def _fix_os_path_join(self, match: re.Match) -> str:
        """Convert os.path.join to Path construction"""
        args = match.group(1)
        # Simple heuristic: if args contain variables, use Path() / syntax
        if "," in args:
            args_list = [arg.strip() for arg in args.split(",")]
            path_parts = " / ".join(args_list)
            return f"Path({path_parts})"
        else:
            return f"Path({args})"

    def _fix_os_path_abspath(self, match: re.Match) -> str:
        """Convert os.path.abspath to Path.resolve()"""
        arg = match.group(1)
        return f"Path({arg}).resolve()"

    def _fix_os_path_dirname(self, match: re.Match) -> str:
        """Convert os.path.dirname to Path.parent"""
        arg = match.group(1)
        return f"Path({arg}).parent"

    def _fix_os_path_basename(self, match: re.Match) -> str:
        """Convert os.path.basename to Path.name"""
        arg = match.group(1)
        return f"Path({arg}).name"

    def _fix_os_path_exists(self, match: re.Match) -> str:
        """Convert os.path.exists to Path.exists()"""
        arg = match.group(1)
        return f"Path({arg}).exists()"

    def _fix_os_path_isdir(self, match: re.Match) -> str:
        """Convert os.path.isdir to Path.is_dir()"""
        arg = match.group(1)
        return f"Path({arg}).is_dir()"

    def _fix_os_path_isfile(self, match: re.Match) -> str:
        """Convert os.path.isfile to Path.is_file()"""
        arg = match.group(1)
        return f"Path({arg}).is_file()"

    def _fix_relative_paths(self, match: re.Match) -> str:
        """Convert relative paths to use Path"""
        path_str = match.group(0)
        return f"str(Path(__file__).parent.parent / {path_str[3:-1]})"

    def _fix_current_dir_paths(self, match: re.Match) -> str:
        """Convert current directory paths to use Path"""
        path_str = match.group(0)
        return f"str(Path(__file__).parent / {path_str[2:-1]})"

    def analyze_file(self, file_path: Path) -> Dict[str, List[str]]:
        """Analyze a file for path handling issues"""
        if not file_path.exists():
            return {}

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        issues = {}
        for pattern, fixer in self.patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                issues[pattern] = matches

        return issues

    def fix_file(self, file_path: Path, dry_run: bool = True) -> Tuple[bool, List[str]]:
        """Fix path handling in a specific file"""
        if not file_path.exists():
            return False, [f"File not found: {file_path}"]

        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        fixed_content = original_content
        changes = []

        # Check if pathlib import is needed
        needs_pathlib = False
        for pattern in self.patterns.keys():
            if re.search(pattern, fixed_content):
                needs_pathlib = True
                break

        # Add pathlib import if needed and not present
        if needs_pathlib and "from pathlib import Path" not in fixed_content:
            import_lines = []
            other_lines = []

            for line in fixed_content.split("\n"):
                if line.startswith("import ") or line.startswith("from "):
                    import_lines.append(line)
                else:
                    other_lines.append(line)

            # Add pathlib import
            import_lines.append("from pathlib import Path")
            changes.append("Added: from pathlib import Path")

            fixed_content = "\n".join(import_lines + [""] + other_lines)

        # Apply pattern fixes
        for pattern, fixer in self.patterns.items():
            old_content = fixed_content
            fixed_content = re.sub(pattern, fixer, fixed_content)
            if old_content != fixed_content:
                matches = re.findall(pattern, old_content)
                changes.append(f"Fixed {len(matches)} instances of {pattern}")

        if fixed_content != original_content:
            if not dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                changes.append(f"File updated: {file_path}")
            else:
                changes.append(f"Would update: {file_path}")
            return True, changes
        else:
            return False, ["No changes needed"]

    def fix_all_files(self, dry_run: bool = True) -> Dict[str, Tuple[bool, List[str]]]:
        """Fix path handling in all specified files"""
        results = {}

        for file_rel_path in self.files_to_fix:
            file_path = self.project_root / file_rel_path
            changed, changes = self.fix_file(file_path, dry_run=dry_run)
            results[file_rel_path] = (changed, changes)

        return results

    def analyze_all_files(self) -> Dict[str, Dict[str, List[str]]]:
        """Analyze all specified files for path handling issues"""
        results = {}

        for file_rel_path in self.files_to_fix:
            file_path = self.project_root / file_rel_path
            issues = self.analyze_file(file_path)
            if issues:
                results[file_rel_path] = issues

        return results


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix path handling inconsistencies")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be fixed without making changes",
    )
    parser.add_argument(
        "--fix", action="store_true", help="Actually fix the files (overrides --dry-run)"
    )
    parser.add_argument("--analyze", action="store_true", help="Only analyze files without fixing")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    fixer = PathFixture(project_root)

    if args.analyze:
        print("🔍 Analyzing files for path handling issues...")
        results = fixer.analyze_all_files()

        if results:
            for file_path, issues in results.items():
                print(f"\n📁 {file_path}:")
                for pattern, matches in issues.items():
                    print(f"  - {pattern}: {len(matches)} occurrences")
                    for match in matches[:3]:  # Show first 3 matches
                        print(f"    - {match}")
                    if len(matches) > 3:
                        print(f"    - ... and {len(matches) - 3} more")
        else:
            print("✅ No path handling issues found!")

        return

    dry_run = args.dry_run and not args.fix

    if dry_run:
        print("🔍 Dry run: analyzing what would be fixed...")
    else:
        print("🔧 Fixing path handling issues...")

    results = fixer.fix_all_files(dry_run=dry_run)

    total_changed = 0
    for file_path, (changed, changes) in results.items():
        if changed:
            total_changed += 1
            status = "📝" if not dry_run else "👀"
            print(f"\n{status} {file_path}:")
            for change in changes:
                print(f"  - {change}")
        else:
            print(f"\n✅ {file_path}: No changes needed")

    if dry_run and total_changed > 0:
        print(f"\n💡 Run with --fix to apply {total_changed} file changes")
    elif not dry_run and total_changed > 0:
        print(f"\n🎉 Successfully fixed {total_changed} files!")
    else:
        print("\n✅ All files are already using consistent path handling!")


if __name__ == "__main__":
    main()
