#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json

from common.orthogonal_config import orthogonal_config


def main():
    # Display available configurations
    print("=== Available Configurations ===")
    available = orthogonal_config.list_available_configs()
    for dim, configs in available.items():
        print(f"{dim}: {configs}")

    print("\n=== Dynamic Configuration Building ===")

    # Dynamic configuration: F2 stocks + YFinance data source + development scenario
    config = orthogonal_config.build_runtime_config(
        stock_list="f2", data_sources=["yfinance"], scenario="development"
    )

    print("F2 + YFinance + Development:")
    print(json.dumps(config, indent=2))

    print("\n=== Alternative Combination ===")

    # Dynamic configuration: M7 stocks + YFinance+SEC data sources + production scenario
    config2 = orthogonal_config.build_runtime_config(
        stock_list="m7", data_sources=["yfinance", "sec_edgar"], scenario="production"
    )

    print("M7 + YFinance+SEC + Production:")
    print(f"Stock count: {config2['stock_list']['count']}")
    print(f"Data sources: {list(config2['data_sources'].keys())}")
    print(f"Processing mode: {config2['scenario']['processing_mode']}")


if __name__ == "__main__":
    main()