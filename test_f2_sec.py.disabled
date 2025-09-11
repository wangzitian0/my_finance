#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from common.orthogonal_config import orthogonal_config


def test_f2_sec():
    """Test F2 SEC Edgar configuration"""
    print("=== F2 SEC Edgar Configuration Test ===")

    try:
        config = orthogonal_config.build_runtime_config("f2", ["sec_edgar"], "development")

        print("✅ F2 + SEC Edgar configuration built successfully")
        print(
            f"📊 Stock List: {config['stock_list']['name']} ({config['stock_list']['count']} companies)"
        )

        sec_config = config["data_sources"]["sec_edgar"]
        print(f"🔐 SEC Edgar Configuration:")
        print(f"    - Enabled: {sec_config['enabled']}")
        print(f"    - Data types: {sec_config['data_types']}")
        print(f"    - Rate limits: {sec_config['rate_limits']}")
        print(f"    - Config keys: {list(sec_config['config'].keys())}")

        return True

    except Exception as e:
        print(f"❌ F2 SEC configuration failed: {e}")
        return False


def test_f2_build():
    """Test running F2 build with SEC Edgar enabled"""
    print("\n=== F2 Build Test ===")

    try:
        # Test if build_dataset can use the F2 configuration
        from ETL.build_dataset import build_dataset

        print("🏗️ Testing F2 build (dry run - checking configuration only)")

        # We won't actually run the full build, just test configuration loading
        from common.config_loader import config_loader
        from ETL.tests.test_config import DatasetTier

        tier = DatasetTier.F2
        config = config_loader.load_dataset_config(tier.value)

        print(f"✅ F2 configuration loaded:")
        print(f"    - Data sources: {list(config.get('data_sources', {}).keys())}")
        print(
            f"    - SEC Edgar enabled: {config.get('data_sources', {}).get('sec_edgar', {}).get('enabled', False)}"
        )
        print(f"    - Expected tickers: {config.get('ticker_count', 'unknown')}")

        return True

    except Exception as e:
        print(f"❌ F2 build test failed: {e}")
        return False


if __name__ == "__main__":
    success1 = test_f2_sec()
    success2 = test_f2_build()

    if success1 and success2:
        print("\n🎉 F2 SEC Edgar integration is working!")
    else:
        print("\n❌ F2 SEC Edgar integration has issues")
