#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.orthogonal_config import orthogonal_config


def test_orthogonal_configs():
    """Test new orthogonal configurations"""
    print("=== Testing Orthogonal Configurations ===")

    for stock_list_name in ["f2", "m7", "n100", "v3k"]:
        try:
            stock_list = orthogonal_config.load_stock_list(stock_list_name)
            print(
                f"✅ {stock_list_name}: {len(stock_list.tickers)} stocks - {stock_list.description}"
            )
        except Exception as e:
            print(f"❌ {stock_list_name}: {e}")

    print("\n=== Testing Data Sources (with fallback) ===")

    for data_source_name in ["yfinance", "sec_edgar"]:
        try:
            data_source = orthogonal_config.load_data_source(data_source_name)
            print(f"✅ {data_source_name}: {data_source.description}")
            print(f"    - Enabled: {data_source.enabled}")
            print(f"    - Data types: {len(data_source.data_types)} types")
        except Exception as e:
            print(f"❌ {data_source_name}: {e}")


def test_dynamic_combinations():
    """Test dynamic configuration building with both systems"""
    print("\n=== Testing Dynamic Combinations ===")

    test_cases = [
        # Using orthogonal configs
        ("f2", ["yfinance"], "development"),
        ("m7", ["yfinance"], "development"),
        # Using legacy configs as fallback
        ("n100", ["yfinance", "sec_edgar"], "production"),
        ("v3k", ["yfinance"], "production"),
    ]

    for stock_list, data_sources, scenario in test_cases:
        try:
            config = orthogonal_config.build_runtime_config(
                stock_list=stock_list, data_sources=data_sources, scenario=scenario
            )

            stock_count = config["stock_list"]["count"]
            sources = list(config["data_sources"].keys())
            mode = config["scenario"]["processing_mode"]

            print(f"✅ {stock_list} + {sources} + {scenario}")
            print(f"    - Stocks: {stock_count}, Mode: {mode}")

        except Exception as e:
            print(f"❌ {stock_list} + {data_sources} + {scenario}: {e}")


def test_available_configs():
    """Test listing available configurations"""
    print("\n=== Available Configurations ===")

    available = orthogonal_config.list_available_configs()
    for dimension, configs in available.items():
        print(f"{dimension}: {configs}")


def main():
    test_available_configs()
    test_orthogonal_configs()
    test_dynamic_combinations()


if __name__ == "__main__":
    main()