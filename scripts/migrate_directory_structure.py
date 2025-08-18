#!/usr/bin/env python3
"""
Directory Structure Migration Script
Migrates legacy directory structures to unified standard format.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.directory_manager import DirectoryManager


def migrate_stage_00_original():
    """Migrate stage_00_original to standard format."""
    print("🔄 Migrating stage_00_original...")

    dm = DirectoryManager()
    base_path = Path("data/stage_00_original")
    date_partition = datetime.now().strftime("%Y%m%d")

    stats = {
        "yfinance_stats": {"files_moved": 0, "tickers_processed": 0, "errors": 0},
        "sec_edgar_stats": {"files_moved": 0, "tickers_processed": 0, "errors": 0},
    }

    # Migrate YFinance data (already in TICKER/ format)
    yfinance_path = base_path / "yfinance"
    if yfinance_path.exists():
        print("  📊 Migrating YFinance data...")
        stats["yfinance_stats"] = dm.migrate_legacy_structure(
            "stage_00_original", yfinance_path, date_partition
        )

    # Migrate SEC Edgar data (complex CIK/filing_type structure)
    sec_edgar_path = base_path / "sec-edgar"
    if sec_edgar_path.exists():
        print("  📋 Migrating SEC Edgar data...")
        stats["sec_edgar_stats"] = migrate_sec_edgar_structure(dm, sec_edgar_path, date_partition)

    return stats


def migrate_sec_edgar_structure(dm: DirectoryManager, source_path: Path, date_partition: str):
    """
    Migrate SEC Edgar structure from CIK-based to ticker-based.

    Legacy: sec-edgar/CIK/filing_type/CIK/filing_type/files
    Standard: stage_00_original/date/TICKER/TICKER_sec_edgar_filing_type_files
    """
    stats = {"files_moved": 0, "tickers_processed": 0, "errors": 0}

    # CIK to Ticker mapping (M7 companies)
    cik_to_ticker = {
        "0000320193": "AAPL",
        "0000789019": "MSFT",
        "0001018724": "AMZN",
        "0001652044": "GOOGL",
        "0001326801": "META",
        "0001318605": "TSLA",
        "0001065280": "NFLX",
    }

    # Process each CIK directory
    for cik_dir in source_path.iterdir():
        if not cik_dir.is_dir():
            continue

        cik = cik_dir.name
        if cik not in cik_to_ticker:
            print(f"  ⚠️  Unknown CIK: {cik} - skipping")
            continue

        ticker = cik_to_ticker[cik]

        try:
            target_dir = dm.create_directory_structure("stage_00_original", ticker, date_partition)

            # Process filing types (10k, 10q, 8k)
            for filing_type_dir in cik_dir.iterdir():
                if not filing_type_dir.is_dir():
                    continue

                filing_type = filing_type_dir.name.lower()

                # Navigate through nested CIK/filing structure
                for nested_cik_dir in filing_type_dir.iterdir():
                    if not nested_cik_dir.is_dir():
                        continue

                    for final_filing_dir in nested_cik_dir.iterdir():
                        if not final_filing_dir.is_dir():
                            continue

                        # Process actual filing files
                        for file_path in final_filing_dir.iterdir():
                            if not file_path.is_file():
                                continue

                            # Create standardized filename
                            new_filename = f"{ticker}_sec_edgar_{filing_type}_{file_path.name}"
                            target_file = target_dir / new_filename

                            # Move file
                            file_path.rename(target_file)
                            stats["files_moved"] += 1

            stats["tickers_processed"] += 1
            print(f"  ✅ Migrated {ticker} ({cik}): {stats['files_moved']} files")

        except Exception as e:
            print(f"  ❌ Error migrating {ticker} ({cik}): {e}")
            stats["errors"] += 1

    return stats


def migrate_stage_03_load():
    """Migrate stage_03_load to standard format."""
    print("🔄 Migrating stage_03_load...")

    dm = DirectoryManager()
    base_path = Path("data/stage_03_load")
    date_partition = datetime.now().strftime("%Y%m%d")

    stats = {"files_moved": 0, "tickers_processed": 0, "errors": 0}

    # Create target structure
    subdirs = [
        "dcf_results",
        "embeddings",
        "graph_embeddings",
        "graph_nodes",
        "graph_rag_cache",
        "vector_index",
    ]

    for subdir in subdirs:
        subdir_path = base_path / subdir
        if not subdir_path.exists():
            continue

        print(f"  📁 Migrating {subdir}...")

        # For stage_03, we need to create a generic structure
        # Since these are cross-ticker artifacts, we'll put them in a special 'SYSTEM' ticker
        try:
            target_dir = dm.create_directory_structure("stage_03_load", "SYSTEM", date_partition)

            for file_path in subdir_path.iterdir():
                if file_path.is_file():
                    new_filename = f"SYSTEM_{subdir}_{file_path.name}"
                    target_file = target_dir / new_filename

                    # Create subdirectory in target if needed
                    (target_dir / subdir).mkdir(exist_ok=True)
                    final_target = target_dir / subdir / file_path.name

                    file_path.rename(final_target)
                    stats["files_moved"] += 1

        except Exception as e:
            print(f"  ❌ Error migrating {subdir}: {e}")
            stats["errors"] += 1

    stats["tickers_processed"] = len(subdirs)
    return stats


def clean_legacy_directories():
    """Clean up empty legacy directories after migration."""
    print("🧹 Cleaning up legacy directories...")

    legacy_paths = [
        Path("data/stage_00_original/yfinance"),
        Path("data/stage_00_original/sec-edgar"),
        Path("data/stage_03_load/dcf_results"),
        Path("data/stage_03_load/embeddings"),
        Path("data/stage_03_load/graph_embeddings"),
        Path("data/stage_03_load/graph_nodes"),
        Path("data/stage_03_load/graph_rag_cache"),
        Path("data/stage_03_load/vector_index"),
    ]

    for path in legacy_paths:
        if path.exists() and path.is_dir():
            try:
                # Only remove if empty
                if not any(path.iterdir()):
                    path.rmdir()
                    print(f"  🗑️  Removed empty directory: {path}")
                else:
                    print(f"  ⚠️  Directory not empty, keeping: {path}")
            except Exception as e:
                print(f"  ❌ Error removing {path}: {e}")


def validate_migration():
    """Validate the migration results."""
    print("✅ Validating migration...")

    dm = DirectoryManager()
    date_partition = datetime.now().strftime("%Y%m%d")

    # Validate stage_00_original
    stage_00_results = dm.validate_structure("stage_00_original", date_partition)
    print(
        f"  📂 stage_00_original: {stage_00_results['tickers_found']} tickers, {stage_00_results['files_found']} files"
    )
    if stage_00_results["issues"]:
        for issue in stage_00_results["issues"]:
            print(f"    ⚠️  {issue}")

    # Validate stage_03_load
    stage_03_results = dm.validate_structure("stage_03_load", date_partition)
    print(
        f"  📂 stage_03_load: {stage_03_results['tickers_found']} tickers, {stage_03_results['files_found']} files"
    )
    if stage_03_results["issues"]:
        for issue in stage_03_results["issues"]:
            print(f"    ⚠️  {issue}")

    return {"stage_00": stage_00_results, "stage_03": stage_03_results}


def main():
    """Main migration process."""
    print("🚀 Starting Directory Structure Migration")
    print("=" * 60)

    # Step 1: Migrate stage_00_original
    stage_00_stats = migrate_stage_00_original()

    # Step 2: Migrate stage_03_load
    stage_03_stats = migrate_stage_03_load()

    # Step 3: Clean up legacy directories
    clean_legacy_directories()

    # Step 4: Validate migration
    validation_results = validate_migration()

    # Summary
    print("\n" + "=" * 60)
    print("📊 Migration Summary:")
    print(
        f"  YFinance: {stage_00_stats['yfinance_stats']['files_moved']} files, {stage_00_stats['yfinance_stats']['tickers_processed']} tickers"
    )
    print(
        f"  SEC Edgar: {stage_00_stats['sec_edgar_stats']['files_moved']} files, {stage_00_stats['sec_edgar_stats']['tickers_processed']} tickers"
    )
    print(
        f"  Stage 03: {stage_03_stats['files_moved']} files, {stage_03_stats['tickers_processed']} categories"
    )

    total_files = (
        stage_00_stats["yfinance_stats"]["files_moved"]
        + stage_00_stats["sec_edgar_stats"]["files_moved"]
        + stage_03_stats["files_moved"]
    )
    print(f"  Total: {total_files} files migrated")

    # Show final structure
    dm = DirectoryManager()
    summary = dm.get_structure_summary()
    print(
        f"\n📁 Final Structure: {summary['total_files']} files across {len(summary['total_tickers'])} tickers"
    )


if __name__ == "__main__":
    main()
