#!/usr/bin/env python3
"""
Directory Structure Modularization Script
Phase 2: Strengthen L1/L2 modularization

This script systematically identifies all directories that need __init__.py files
and creates them with appropriate module documentation.

Issue #256: Directory structure adjustment Phase 2
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def find_python_directories(root_path: Path) -> List[Path]:
    """
    Find all directories that contain Python files or subdirectories with Python files.
    These should be Python packages with __init__.py files.
    """
    python_dirs = set()
    
    # Walk through all directories
    for root, dirs, files in os.walk(root_path):
        root_path_obj = Path(root)
        
        # Skip hidden directories, build artifacts, and virtual environments
        dirs_to_skip = {'.git', '__pycache__', '.pytest_cache', '.pixi', 'build_data', 
                       '.venv', 'venv', 'node_modules', '.mypy_cache', '.coverage'}
        dirs[:] = [d for d in dirs if d not in dirs_to_skip]
        
        # Check if directory has Python files
        has_python_files = any(f.endswith('.py') for f in files)
        
        # Check if directory has subdirectories with Python files
        has_python_subdirs = False
        for subdir in dirs:
            subdir_path = root_path_obj / subdir
            if any(subdir_path.glob('**/*.py')):
                has_python_subdirs = True
                break
        
        # Add to python_dirs if it contains Python content
        if has_python_files or has_python_subdirs:
            python_dirs.add(root_path_obj)
    
    return sorted(python_dirs)


def get_missing_init_files(python_dirs: List[Path]) -> List[Path]:
    """Find directories that need __init__.py files."""
    missing_init_files = []
    
    for dir_path in python_dirs:
        init_file = dir_path / '__init__.py'
        if not init_file.exists():
            missing_init_files.append(init_file)
    
    return missing_init_files


def generate_init_content(init_file_path: Path) -> str:
    """Generate appropriate __init__.py content based on directory location and content."""
    dir_path = init_file_path.parent
    dir_name = dir_path.name
    relative_path = dir_path.relative_to(Path.cwd())
    
    # Get Python files in the directory
    python_files = [f.stem for f in dir_path.glob('*.py') if f.name != '__init__.py']
    
    # Get subdirectories with Python files
    subdirs = [d.name for d in dir_path.iterdir() 
               if d.is_dir() and any(d.glob('**/*.py')) 
               and d.name not in {'__pycache__', '.pytest_cache'}]
    
    # Generate docstring based on location
    if len(relative_path.parts) == 1:
        # L1 directory
        docstring = f'"""\n{dir_name.title().replace("_", " ")} Module\n\nTop-level module for {dir_name} functionality.\n"""'
    else:
        # L2+ directory
        parent_module = relative_path.parts[0]
        docstring = f'"""\n{dir_name.title().replace("_", " ")} submodule of {parent_module}\n\nProvides {dir_name.replace("_", " ")} functionality.\n"""'
    
    # Start building content
    content = f"#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n{docstring}\n\n"
    
    # Add imports if there are Python files or important subdirectories
    imports = []
    all_exports = []
    
    # Import from Python files (but be conservative to avoid circular imports)
    for py_file in python_files:
        if py_file in {'main', 'cli', 'app', 'api', 'server'}:
            # Skip main/entry point files to avoid circular imports
            continue
        imports.append(f"# from .{py_file} import *")
        
    # Import from important subdirectories
    for subdir in subdirs:
        if subdir in {'core', 'components', 'utils', 'processors', 'managers'}:
            imports.append(f"# from .{subdir} import *")
    
    if imports:
        content += "# Import statements (uncomment as needed to avoid circular imports):\n"
        content += "\n".join(imports)
        content += "\n\n"
    
    # Add __all__ placeholder
    if python_files or subdirs:
        content += "# Define public interface\n"
        content += "__all__ = [\n"
        content += "    # Add public exports here\n"
        content += "]\n"
    
    return content


def create_init_files(missing_init_files: List[Path], dry_run: bool = False) -> None:
    """Create missing __init__.py files with appropriate content."""
    created_count = 0
    
    print(f"\n{'DRY RUN: ' if dry_run else ''}Creating __init__.py files...")
    print("=" * 60)
    
    for init_file in missing_init_files:
        try:
            content = generate_init_content(init_file)
            
            if dry_run:
                print(f"WOULD CREATE: {init_file.relative_to(Path.cwd())}")
                print(f"Content preview (first 200 chars):\n{content[:200]}...\n")
            else:
                # Create parent directory if it doesn't exist
                init_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Write the file
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"CREATED: {init_file.relative_to(Path.cwd())}")
                created_count += 1
        
        except Exception as e:
            print(f"ERROR creating {init_file}: {e}")
    
    if not dry_run:
        print(f"\nSUCCESS: Created {created_count} __init__.py files")
    else:
        print(f"\nDRY RUN: Would create {len(missing_init_files)} __init__.py files")


def analyze_directory_structure() -> None:
    """Analyze and report on the current directory structure."""
    root_path = Path.cwd()
    
    print("Directory Structure Analysis")
    print("=" * 50)
    
    # Find all Python directories
    python_dirs = find_python_directories(root_path)
    print(f"Found {len(python_dirs)} directories with Python content")
    
    # Check for missing __init__.py files
    missing_init_files = get_missing_init_files(python_dirs)
    print(f"Missing __init__.py files: {len(missing_init_files)}")
    
    # Categorize by L1/L2 level
    l1_missing = []
    l2_missing = []
    l3_plus_missing = []
    
    for init_file in missing_init_files:
        relative_path = init_file.parent.relative_to(root_path)
        parts_count = len(relative_path.parts)
        
        if parts_count == 1:
            l1_missing.append(init_file)
        elif parts_count == 2:
            l2_missing.append(init_file)
        else:
            l3_plus_missing.append(init_file)
    
    print(f"\nMissing by level:")
    print(f"  L1 directories: {len(l1_missing)}")
    print(f"  L2 directories: {len(l2_missing)}")
    print(f"  L3+ directories: {len(l3_plus_missing)}")
    
    # Show missing files by category
    if l1_missing:
        print(f"\nL1 Missing __init__.py files:")
        for init_file in l1_missing:
            print(f"  - {init_file.relative_to(root_path)}")
    
    if l2_missing:
        print(f"\nL2 Missing __init__.py files:")
        for init_file in l2_missing:
            print(f"  - {init_file.relative_to(root_path)}")
    
    return missing_init_files


def main():
    """Main execution function."""
    print("L1/L2 Modularization Script - Issue #256 Phase 2")
    print("=" * 60)
    
    # Analyze current structure
    missing_init_files = analyze_directory_structure()
    
    if not missing_init_files:
        print("\n✅ All directories already have __init__.py files!")
        return
    
    # Ask for confirmation
    print(f"\nReady to create {len(missing_init_files)} __init__.py files")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        create_init_files(missing_init_files, dry_run=True)
    elif len(sys.argv) > 1 and sys.argv[1] == '--execute':
        create_init_files(missing_init_files, dry_run=False)
    else:
        print("\nUsage:")
        print("  python modularization_script.py --dry-run   # Preview changes")
        print("  python modularization_script.py --execute   # Create files")
        
        response = input("\nProceed with creating files? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            create_init_files(missing_init_files, dry_run=False)
        else:
            print("Operation cancelled.")


if __name__ == "__main__":
    main()