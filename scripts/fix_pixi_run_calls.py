#!/usr/bin/env python3
"""
Script to replace 'pixi run' calls with 'p3' equivalents throughout the codebase.
This enforces the use of our unified p3 CLI instead of direct pixi calls.

Updated for simplified P3 system with only 8 commands:
ready, reset, check, test, ship, debug, build, version
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Mapping of pixi run commands to p3 equivalents (simplified to 8 commands)
COMMAND_MAPPING = {
    # Core 8 workflow commands
    "p3 ready": "p3 ready",
    "p3 reset": "p3 reset", 
    "p3 check": "p3 check",
    "p3 check f2": "p3 check f2",
    "p3 check m7": "p3 check m7",
    "p3 test": "p3 test",
    "p3 test f2": "p3 test f2",
    "p3 test m7": "p3 test m7",
    "p3 test n100": "p3 test n100",
    "p3 test v3k": "p3 test v3k",
    "p3 ship": "p3 ship",
    "p3 debug": "p3 debug",
    "p3 build": "p3 build",
    "p3 build f2": "p3 build f2",
    "p3 build m7": "p3 build m7", 
    "p3 build n100": "p3 build n100",
    "p3 build v3k": "p3 build v3k",
    "p3 version": "p3 version",
    
    # Legacy command mappings to new equivalents
    "p3 e2e": "p3 test",
    "p3 e2e f2": "p3 test f2",
    "p3 e2e m7": "p3 test m7",
    "p3 format": "p3 check",
    "p3 lint": "p3 check", 
    "p3 env reset": "p3 reset",
    "p3 env setup": "p3 ready",
    "p3 env start": "p3 ready",
    "p3 status": "p3 debug",
    "p3 verify-env": "p3 debug",
}


def find_files_to_process() -> List[Path]:
    """Find all Python, shell, and config files to process."""
    project_root = Path(__file__).parent.parent
    files = []
    
    # Include patterns
    patterns = ["*.py", "*.sh", "*.yml", "*.yaml", "*.toml", "*.md"]
    
    # Exclude patterns
    exclude_dirs = {
        ".git", "__pycache__", ".pixi", ".pytest_cache", 
        "node_modules", ".mypy_cache", "build_data", "scripts/p3"
    }
    
    print(f"🔍 Searching in: {project_root}")
    
    for pattern in patterns:
        for file_path in project_root.rglob(pattern):
            # Skip if in excluded directory
            if any(excl in str(file_path) for excl in exclude_dirs):
                continue
            # Skip if not a file
            if not file_path.is_file():
                continue
                
            files.append(file_path)
    
    print(f"📁 Found {len(files)} files to process")
    return files


def process_file(file_path: Path) -> Tuple[int, List[str]]:
    """Process a single file and replace commands."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return 0, []
    
    original_content = content
    replacements = []
    
    # Apply command mappings
    for old_cmd, new_cmd in COMMAND_MAPPING.items():
        if old_cmd in content and old_cmd != new_cmd:
            content = content.replace(old_cmd, new_cmd)
            if old_cmd != new_cmd:
                replacements.append(f"{old_cmd} → {new_cmd}")
    
    # Write back if changed
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return len(replacements), replacements
        except PermissionError:
            return 0, []
    
    return 0, []


def main():
    """Main execution function."""
    print("🔧 Fixing pixi run calls to use p3 commands...")
    print("📋 Simplified P3 system with 8 commands: ready, reset, check, test, ship, debug, build, version")
    
    files = find_files_to_process()
    total_files_changed = 0
    total_replacements = 0
    
    for file_path in files:
        num_replacements, replacements = process_file(file_path)
        
        if num_replacements > 0:
            total_files_changed += 1
            total_replacements += num_replacements
            print(f"✅ {file_path}: {num_replacements} replacements")
            for replacement in replacements:
                print(f"   {replacement}")
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {len(files)}")
    print(f"   Files changed: {total_files_changed}")
    print(f"   Total replacements: {total_replacements}")
    
    if total_replacements > 0:
        print("✅ Command fixing complete!")
    else:
        print("ℹ️  No changes needed - all commands already using p3!")


if __name__ == "__main__":
    main()