#!/usr/bin/env python3
"""
Clean up obsolete files after data structure migration.
Removes old directories and files that are no longer needed.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def cleanup_obsolete_files(base_path: str = "/Users/SP14016/zitian/my_finance") -> None:
    """Clean up obsolete files and directories"""
    base_dir = Path(base_path)

    # Files and directories to remove (if they exist and are safe to remove)
    obsolete_paths = [
        # Empty test directories
        "test_yahoo",
        # Legacy build artifacts that might be outdated
        "t",  # single file that appears to be temporary
        # Any __pycache__ directories not in important locations
        # We'll handle these separately to be more selective
    ]

    removed_count = 0

    for obsolete_path in obsolete_paths:
        full_path = base_dir / obsolete_path

        if not full_path.exists():
            logger.debug(f"Path does not exist: {full_path}")
            continue

        try:
            if full_path.is_file():
                full_path.unlink()
                logger.info(f"Removed file: {full_path}")
                removed_count += 1
            elif full_path.is_dir():
                # Only remove if directory is empty or contains only safe files
                if is_safe_to_remove_directory(full_path):
                    shutil.rmtree(full_path)
                    logger.info(f"Removed directory: {full_path}")
                    removed_count += 1
                else:
                    logger.warning(f"Skipped non-empty directory: {full_path}")
        except Exception as e:
            logger.error(f"Failed to remove {full_path}: {e}")

    # Clean up __pycache__ directories selectively
    pycache_count = cleanup_pycache_directories(base_dir)
    removed_count += pycache_count

    logger.info(f"Cleanup completed. Removed {removed_count} items.")


def is_safe_to_remove_directory(dir_path: Path) -> bool:
    """Check if directory is safe to remove"""
    # Don't remove if it contains important files
    important_extensions = {".py", ".yml", ".yaml", ".md", ".json", ".txt"}

    try:
        for item in dir_path.rglob("*"):
            if item.is_file():
                if item.suffix.lower() in important_extensions:
                    return False
                # Check if it's a data file that might be important
                if item.parent.name in {"config", "scripts", "ETL", "spider", "common"}:
                    return False
    except Exception:
        # If we can't check contents, err on the side of caution
        return False

    return True


def cleanup_pycache_directories(base_dir: Path) -> int:
    """Clean up __pycache__ directories"""
    removed_count = 0

    # Find all __pycache__ directories
    pycache_dirs = list(base_dir.rglob("__pycache__"))

    for pycache_dir in pycache_dirs:
        # Skip if it's in a virtual environment or important location
        if any(part in str(pycache_dir) for part in [".pixi", "venv", "env", ".git"]):
            continue

        try:
            shutil.rmtree(pycache_dir)
            logger.info(f"Removed __pycache__: {pycache_dir}")
            removed_count += 1
        except Exception as e:
            logger.warning(f"Failed to remove __pycache__ {pycache_dir}: {e}")

    return removed_count


def cleanup_empty_directories(base_dir: Path) -> int:
    """Remove empty directories (excluding important structure)"""
    removed_count = 0

    # Directories that should be preserved even if empty
    preserve_dirs = {
        "data/stage_01_extract",
        "data/stage_02_transform",
        "data/stage_03_load",
        "data/build",
        "data/config",
        "data/reports",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "tests/fixtures",
    }

    # Convert to absolute paths for comparison
    preserve_paths = {(base_dir / path).resolve() for path in preserve_dirs}

    # Walk through directories bottom-up to remove empty dirs
    for dir_path in reversed(list(base_dir.rglob("*"))):
        if not dir_path.is_dir():
            continue

        # Skip if it's a preserved directory
        if dir_path.resolve() in preserve_paths:
            continue

        # Skip if it's in .git or .pixi
        if any(part in str(dir_path) for part in [".git", ".pixi", "__pycache__"]):
            continue

        try:
            # Check if directory is empty
            if not any(dir_path.iterdir()):
                dir_path.rmdir()
                logger.info(f"Removed empty directory: {dir_path}")
                removed_count += 1
        except OSError:
            # Directory not empty or permission issue
            continue
        except Exception as e:
            logger.warning(f"Failed to remove empty directory {dir_path}: {e}")

    return removed_count


def main():
    """Main cleanup function"""
    logger.info("Starting obsolete file cleanup...")

    try:
        cleanup_obsolete_files()

        # Clean up empty directories last
        base_dir = Path("/Users/SP14016/zitian/my_finance")
        empty_count = cleanup_empty_directories(base_dir)
        logger.info(f"Removed {empty_count} empty directories")

        logger.info("Cleanup completed successfully!")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
