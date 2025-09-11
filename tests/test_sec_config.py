#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.orthogonal_config import orthogonal_config


def test_sec_edgar_config():
    """Test SEC Edgar configuration through orthogonal system"""
    print("=== Testing SEC Edgar Configuration ===")

    try:
        config = orthogonal_config.build_runtime_config("f2", ["sec_edgar"], "development")

        sec_config = config["data_sources"]["sec_edgar"]
        print(f"✅ SEC Edgar Config loaded:")
        print(f"    - Enabled: {sec_config['enabled']}")
        print(f"    - Data types: {sec_config['data_types']}")
        print(f"    - Rate limits: {sec_config['rate_limits']}")
        print(f"    - API config keys: {list(sec_config['config'].keys())}")

        return True

    except Exception as e:
        print(f"❌ SEC Edgar config failed: {e}")
        return False


def test_build_dataset_integration():
    """Test if build_dataset.py can use the SEC configuration"""
    print("\n=== Testing Build Dataset Integration ===")

    try:
        # Import the build_dataset module
        from ETL.build_dataset import build_dataset
        from ETL.tests.test_config import DatasetTier

        # Check if F2 tier exists and can be used
        tier = DatasetTier.F2
        print(f"✅ DatasetTier.F2 found: {tier.value}")

        # Try to load the config (without actually running the build)
        from common.config_loader import config_loader

        config = config_loader.load_dataset_config(tier.value)
        print(f"✅ Config loaded for {tier.value}")
        print(f"    - Data sources: {list(config.get('data_sources', {}).keys())}")
        print(
            f"    - SEC Edgar enabled: {config.get('data_sources', {}).get('sec_edgar', {}).get('enabled', False)}"
        )

        return True

    except Exception as e:
        print(f"❌ Build dataset integration failed: {e}")
        return False


if __name__ == "__main__":
    success = test_sec_edgar_config()
    success &= test_build_dataset_integration()

    if success:
        print("\n🎉 SEC Edgar configuration system is working!")
    else:
        print("\n❌ SEC Edgar configuration has issues")