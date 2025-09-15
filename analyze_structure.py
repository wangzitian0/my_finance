#!/usr/bin/env python3
"""
Analyze current directory structure for Issue #256 consolidation
"""
import os
from pathlib import Path


def analyze_directory_structure():
    """Analyze current directory structure"""
    root = Path('.')
    
    print("CURRENT ROOT DIRECTORIES:")
    print("=" * 50)
    
    dirs = []
    for item in root.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            dirs.append(item)
    
    # Sort directories
    dirs.sort(key=lambda x: x.name.lower())
    
    # Analyze each directory
    for dir_path in dirs:
        file_count = 0
        subdir_count = 0
        python_files = 0
        
        try:
            for item in dir_path.iterdir():
                if item.is_dir():
                    subdir_count += 1
                elif item.is_file():
                    file_count += 1
                    if item.suffix == '.py':
                        python_files += 1
        except PermissionError:
            print(f"{dir_path.name:<20} [PERMISSION DENIED]")
            continue
            
        print(f"{dir_path.name:<20} Files: {file_count:>3}, Subdirs: {subdir_count:>2}, Python: {python_files:>3}")
    
    print("\n" + "=" * 50)
    print(f"TOTAL L1 DIRECTORIES: {len(dirs)}")
    
    # Identify small directories (candidates for merging)
    print("\nSMALL DIRECTORIES (<=5 files, candidates for merging):")
    print("-" * 50)
    small_dirs = []
    for dir_path in dirs:
        try:
            file_count = sum(1 for item in dir_path.iterdir() if item.is_file())
            if file_count <= 5:
                small_dirs.append((dir_path.name, file_count))
        except PermissionError:
            continue
    
    for name, count in sorted(small_dirs):
        print(f"{name:<20} {count} files")
    
    print(f"\nSMALL DIRECTORIES COUNT: {len(small_dirs)}")
    return dirs, small_dirs


if __name__ == "__main__":
    analyze_directory_structure()