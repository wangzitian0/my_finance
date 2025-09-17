#!/usr/bin/env python3
"""
Data structure migration script
Migrates data structure to support P3 workflow
"""

import os
import shutil
from pathlib import Path

def migrate_data_structure():
    """Migrate data structure for P3 workflow"""
    print("🔄 Starting data structure migration...")

    # Create required directories
    directories = [
        "data/stage_01_extract/yfinance",
        "data/stage_01_extract/sec_edgar",
        "data/stage_02_transform",
        "data/stage_03_clean",
        "build_data/stage_00_raw",
        "build_data/stage_01_daily_delta",
        "build_data/stage_04_query_results",
        "common/config"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

    print("✅ Data structure migration completed")

if __name__ == "__main__":
    migrate_data_structure()