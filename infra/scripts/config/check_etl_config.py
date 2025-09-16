#!/usr/bin/env python3
"""
Unified ETL configuration check script
Support checking all types of ETL configurations: stock lists, data sources, scenarios

Usage:
    python scripts/config/check_etl_config.py --stock-list f2
    python scripts/config/check_etl_config.py --stock-list v3k --details
    python scripts/config/check_etl_config.py --data-source yfinance
    python scripts/config/check_etl_config.py --scenario development
    python scripts/config/check_etl_config.py --all
    python scripts/config/check_etl_config.py --runtime f2 yfinance development

Principle: One script, multiple configurations (Issue #278)
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from common.etl_loader import (
        build_etl_config,
        etl_loader,
        list_available_configs,
        load_data_source,
        load_scenario,
        load_stock_list,
    )
except ImportError as e:
    print(f"❌ Unable to import ETL configuration loader: {e}")
    print(
        "💡 Please ensure ETL configuration migration is complete: python scripts/migrate_etl_config.py --migrate"
    )
    sys.exit(1)


def check_stock_list(name: str, details: bool = False):
    """Check stock list configuration"""
    print(f"📊 Checking stock list: {name}")

    try:
        stock_config = load_stock_list(name)

        print(f"   Name: {stock_config.name}")
        print(f"   Description: {stock_config.description}")
        print(f"   Tier: {stock_config.tier}")
        print(f"   Stock count: {stock_config.count}")
        print(f"   Max size: {stock_config.max_size_mb}MB")

        if details:
            print(f"   Stock tickers: {', '.join(stock_config.tickers)}")

            print("   Company details:")
            for ticker, info in stock_config.companies.items():
                sector = info.get("sector", "N/A")
                industry = info.get("industry", "N/A")
                name = info.get("name", "N/A")
                print(f"      {ticker}: {name} ({sector} - {industry})")
        else:
            print(f"   First 5 stocks: {', '.join(stock_config.tickers[:5])}")
            if len(stock_config.tickers) > 10:
                print(f"   Last 5 stocks: {', '.join(stock_config.tickers[-5:])}")

        print("   ✅ Stock list configuration OK")

    except Exception as e:
        print(f"   ❌ Stock list check failed: {e}")


def check_data_source(name: str, details: bool = False):
    """Check data source configuration"""
    print(f"🔌 Checking data source: {name}")

    try:
        source_config = load_data_source(name)

        print(f"   Name: {source_config.name}")
        print(f"   Description: {source_config.description}")
        print(f"   Status: {'Enabled' if source_config.enabled else 'Disabled'}")
        print(f"   Data types: {', '.join(source_config.data_types)}")

        if details:
            print("   API configuration:")
            for key, value in source_config.api_config.items():
                if isinstance(value, dict):
                    print(f"      {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"         {sub_key}: {sub_value}")
                else:
                    print(f"      {key}: {value}")

            print("   Rate limits:")
            for key, value in source_config.rate_limits.items():
                print(f"      {key}: {value}")

            print("   Output format:")
            for key, value in source_config.output_format.items():
                print(f"      {key}: {value}")

        print("   ✅ Data source configuration OK")

    except Exception as e:
        print(f"   ❌ Data source check failed: {e}")


def check_scenario(name: str, details: bool = False):
    """Check scenario configuration"""
    print(f"🎯 Checking scenario: {name}")

    try:
        scenario_config = load_scenario(name)

        print(f"   Name: {scenario_config.name}")
        print(f"   Description: {scenario_config.description}")
        print(f"   Processing mode: {scenario_config.processing_mode}")
        print(f"   Available data sources: {', '.join(scenario_config.data_sources)}")
        print(f"   Output formats: {', '.join(scenario_config.output_formats)}")

        if details:
            print("   Quality thresholds:")
            for key, value in scenario_config.quality_thresholds.items():
                print(f"      {key}: {value}")

            print("   Resource limits:")
            for key, value in scenario_config.resource_limits.items():
                print(f"      {key}: {value}")

            print("   Optimization settings:")
            for key, value in scenario_config.optimizations.items():
                print(f"      {key}: {value}")

        print("   ✅ Scenario configuration OK")

    except Exception as e:
        print(f"   ❌ Scenario check failed: {e}")


def check_runtime_config(stock_list: str, data_sources: list, scenario: str):
    """Check runtime configuration combination"""
    print(f"🔧 Checking runtime configuration combination")
    print(f"   Stock list: {stock_list}")
    print(f"   Data sources: {', '.join(data_sources)}")
    print(f"   Scenario: {scenario}")

    try:
        runtime_config = build_etl_config(stock_list, data_sources, scenario)

        print(f"   ✅ Configuration combination: {runtime_config.combination}")
        print(f"   Stock count: {runtime_config.ticker_count}")
        print(f"   Enabled data sources: {', '.join(runtime_config.enabled_sources)}")
        print(f"   Processing mode: {runtime_config.scenario.processing_mode}")

        # Validate configuration consistency
        if set(data_sources) != set(runtime_config.enabled_sources):
            print(f"   ⚠️ Warning: Requested data sources don't match enabled data sources")
            print(f"       Requested: {set(data_sources)}")
            print(f"       Enabled: {set(runtime_config.enabled_sources)}")

        print("   ✅ Runtime configuration combination OK")

    except Exception as e:
        print(f"   ❌ Runtime configuration check failed: {e}")


def check_all_configs():
    """Check all available configurations"""
    print("🔍 Checking all available configurations")

    try:
        configs = list_available_configs()

        print(f"📋 Available configurations overview:")
        for config_type, names in configs.items():
            print(f"   {config_type}: {', '.join(names)} (total: {len(names)})")

        print("\n🧪 Configuration validity test:")

        # Test each stock list
        print("   Stock lists:")
        for name in configs["stock_lists"]:
            try:
                config = load_stock_list(name)
                print(f"      ✅ {name}: {config.count} stocks")
            except Exception as e:
                print(f"      ❌ {name}: {e}")

        # Test each data source
        print("   Data sources:")
        for name in configs["data_sources"]:
            try:
                config = load_data_source(name)
                status = "Enabled" if config.enabled else "Disabled"
                print(f"      ✅ {name}: {status}")
            except Exception as e:
                print(f"      ❌ {name}: {e}")

        # Test each scenario
        print("   Scenarios:")
        for name in configs["scenarios"]:
            try:
                config = load_scenario(name)
                print(f"      ✅ {name}: {config.processing_mode} mode")
            except Exception as e:
                print(f"      ❌ {name}: {e}")

        # Test common configuration combinations
        print("   Common configuration combinations:")
        test_combinations = [
            ("f2", ["yfinance"], "development"),
            ("m7", ["yfinance", "sec_edgar"], "development"),
            ("v3k", ["yfinance", "sec_edgar"], "production"),
        ]

        for stock_list, data_sources, scenario in test_combinations:
            try:
                config = build_etl_config(stock_list, data_sources, scenario)
                print(f"      ✅ {config.combination}")
            except Exception as e:
                print(f"      ❌ {stock_list}_{'+'.join(data_sources)}_{scenario}: {e}")

        print("\n✅ All configuration checks completed")

    except Exception as e:
        print(f"❌ Configuration check failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Unified ETL configuration check tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
    # Check specific stock list
    python scripts/config/check_etl_config.py --stock-list f2
    python scripts/config/check_etl_config.py --stock-list v3k --details

    # Check data source
    python scripts/config/check_etl_config.py --data-source yfinance --details

    # Check scenario
    python scripts/config/check_etl_config.py --scenario development

    # Check runtime configuration combination
    python scripts/config/check_etl_config.py --runtime f2 yfinance development

    # Check all configurations
    python scripts/config/check_etl_config.py --all
        """,
    )

    parser.add_argument(
        "--stock-list", help="Check specified stock list configuration (f2, m7, n100, v3k)"
    )
    parser.add_argument(
        "--data-source", help="Check specified data source configuration (yfinance, sec_edgar)"
    )
    parser.add_argument(
        "--scenario", help="Check specified scenario configuration (development, production)"
    )
    parser.add_argument(
        "--runtime",
        nargs=3,
        metavar=("STOCK_LIST", "DATA_SOURCE", "SCENARIO"),
        help="Check runtime configuration combination (e.g.: f2 yfinance development)",
    )
    parser.add_argument("--all", action="store_true", help="Check all available configurations")
    parser.add_argument("--details", action="store_true", help="Show detailed information")

    args = parser.parse_args()

    if not any([args.stock_list, args.data_source, args.scenario, args.runtime, args.all]):
        parser.print_help()
        return

    print("🎯 ETL Configuration Check Tool")
    print("=" * 50)

    try:
        if args.stock_list:
            check_stock_list(args.stock_list, args.details)

        elif args.data_source:
            check_data_source(args.data_source, args.details)

        elif args.scenario:
            check_scenario(args.scenario, args.details)

        elif args.runtime:
            stock_list, data_source, scenario = args.runtime
            check_runtime_config(stock_list, [data_source], scenario)

        elif args.all:
            check_all_configs()

    except KeyboardInterrupt:
        print("\n⏹️ Check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error occurred during check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
