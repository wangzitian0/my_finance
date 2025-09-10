#!/usr/bin/env python3
"""
Display configuration summary after unification.

Migrated from scripts/config_summary.py as part of infrastructure modularization.
"""

from common.unified_config_loader import UnifiedConfigLoader
from ETL.tests.test_config import DatasetTier


def show_config_summary():
    """Display unified configuration summary"""
    loader = UnifiedConfigLoader()

    print("📊 Unified Configuration Summary:")
    print("=" * 60)

    for tier in [DatasetTier.F2, DatasetTier.M7, DatasetTier.N100, DatasetTier.V3K]:
        config = loader.load_config(tier)
        cik_count = len(loader.get_cik_mapping(tier))

        print(f"🔸 {tier.value.upper()}: {config.dataset_name} ({config.cli_alias})")
        print(f"   Companies: {len(config.companies)}, SEC Enabled: {loader.is_sec_enabled(tier)}")
        print(f"   CIKs Available: {cik_count}, Timeout: {loader.get_timeout_seconds(tier)}s")
        print()


if __name__ == "__main__":
    show_config_summary()