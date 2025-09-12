#!/usr/bin/env python3
"""
Clean up temporary files created during modularization.
"""

import os
from pathlib import Path

# Remove temporary files
temp_files = [
    "modularization_script.py",
    "modularization_validation.py",
    "cleanup_temp_files.py"  # Self-destruct this file too
]

for temp_file in temp_files:
    temp_path = Path(temp_file)
    if temp_path.exists():
        temp_path.unlink()
        print(f"Removed {temp_file}")
    else:
        print(f"File {temp_file} not found")

print("Cleanup complete!")