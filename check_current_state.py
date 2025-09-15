#!/usr/bin/env python3
"""Check current directory state before consolidation"""
import os
from pathlib import Path

root = Path(".")
print("CURRENT STATE ANALYSIS:")
print("=" * 50)

# List all L1 directories
dirs = [d.name for d in root.iterdir() if d.is_dir() and not d.name.startswith(".")]
dirs.sort()

print(f"Current L1 directories ({len(dirs)}):")
for d in dirs:
    dir_path = root / d
    try:
        files = [f for f in dir_path.iterdir() if f.is_file()]
        subdirs = [f for f in dir_path.iterdir() if f.is_dir()]
        print(f"  {d:<20} Files: {len(files):>2}, Subdirs: {len(subdirs):>2}")
    except:
        print(f"  {d:<20} [ERROR accessing]")

print(f"\nTOTAL DIRECTORIES: {len(dirs)}")

# Check specific directories we want to consolidate
check_dirs = [
    "graph_rag",
    "evaluation",
    "dts",
    "templates",
    "agents",
    "scripts",
    "releases",
    "dcf_engine",
]
print(f"\nCONSOLIDATION TARGETS:")
for check_dir in check_dirs:
    exists = (root / check_dir).exists()
    print(f"  {check_dir:<15} {'EXISTS' if exists else 'NOT FOUND'}")
