#!/usr/bin/env python3
"""
统一的ETL配置检查脚本
支持检查所有类型的ETL配置：股票列表、数据源、场景

用法:
    python scripts/config/check_etl_config.py --stock-list f2
    python scripts/config/check_etl_config.py --stock-list v3k --details
    python scripts/config/check_etl_config.py --data-source yfinance
    python scripts/config/check_etl_config.py --scenario development
    python scripts/config/check_etl_config.py --all
    python scripts/config/check_etl_config.py --runtime f2 yfinance development

原则: 一套代码，多套配置 (Issue #278)
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
    print(f"❌ 无法导入ETL配置加载器: {e}")
    print("💡 请确保已完成ETL配置迁移: python scripts/migrate_etl_config.py --migrate")
    sys.exit(1)


def check_stock_list(name: str, details: bool = False):
    """检查股票列表配置"""
    print(f"📊 检查股票列表: {name}")

    try:
        stock_config = load_stock_list(name)

        print(f"   名称: {stock_config.name}")
        print(f"   描述: {stock_config.description}")
        print(f"   层级: {stock_config.tier}")
        print(f"   股票数量: {stock_config.count}")
        print(f"   最大大小: {stock_config.max_size_mb}MB")

        if details:
            print(f"   股票代码: {', '.join(stock_config.tickers)}")

            print("   公司详情:")
            for ticker, info in stock_config.companies.items():
                sector = info.get("sector", "N/A")
                industry = info.get("industry", "N/A")
                name = info.get("name", "N/A")
                print(f"      {ticker}: {name} ({sector} - {industry})")
        else:
            print(f"   前5个股票: {', '.join(stock_config.tickers[:5])}")
            if len(stock_config.tickers) > 10:
                print(f"   后5个股票: {', '.join(stock_config.tickers[-5:])}")

        print("   ✅ 股票列表配置正常")

    except Exception as e:
        print(f"   ❌ 股票列表检查失败: {e}")


def check_data_source(name: str, details: bool = False):
    """检查数据源配置"""
    print(f"🔌 检查数据源: {name}")

    try:
        source_config = load_data_source(name)

        print(f"   名称: {source_config.name}")
        print(f"   描述: {source_config.description}")
        print(f"   状态: {'启用' if source_config.enabled else '禁用'}")
        print(f"   数据类型: {', '.join(source_config.data_types)}")

        if details:
            print("   API配置:")
            for key, value in source_config.api_config.items():
                if isinstance(value, dict):
                    print(f"      {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"         {sub_key}: {sub_value}")
                else:
                    print(f"      {key}: {value}")

            print("   速率限制:")
            for key, value in source_config.rate_limits.items():
                print(f"      {key}: {value}")

            print("   输出格式:")
            for key, value in source_config.output_format.items():
                print(f"      {key}: {value}")

        print("   ✅ 数据源配置正常")

    except Exception as e:
        print(f"   ❌ 数据源检查失败: {e}")


def check_scenario(name: str, details: bool = False):
    """检查场景配置"""
    print(f"🎯 检查场景: {name}")

    try:
        scenario_config = load_scenario(name)

        print(f"   名称: {scenario_config.name}")
        print(f"   描述: {scenario_config.description}")
        print(f"   处理模式: {scenario_config.processing_mode}")
        print(f"   可用数据源: {', '.join(scenario_config.data_sources)}")
        print(f"   输出格式: {', '.join(scenario_config.output_formats)}")

        if details:
            print("   质量阈值:")
            for key, value in scenario_config.quality_thresholds.items():
                print(f"      {key}: {value}")

            print("   资源限制:")
            for key, value in scenario_config.resource_limits.items():
                print(f"      {key}: {value}")

            print("   优化设置:")
            for key, value in scenario_config.optimizations.items():
                print(f"      {key}: {value}")

        print("   ✅ 场景配置正常")

    except Exception as e:
        print(f"   ❌ 场景检查失败: {e}")


def check_runtime_config(stock_list: str, data_sources: list, scenario: str):
    """检查运行时配置组合"""
    print(f"🔧 检查运行时配置组合")
    print(f"   股票列表: {stock_list}")
    print(f"   数据源: {', '.join(data_sources)}")
    print(f"   场景: {scenario}")

    try:
        runtime_config = build_etl_config(stock_list, data_sources, scenario)

        print(f"   ✅ 配置组合: {runtime_config.combination}")
        print(f"   股票数量: {runtime_config.ticker_count}")
        print(f"   启用的数据源: {', '.join(runtime_config.enabled_sources)}")
        print(f"   处理模式: {runtime_config.scenario.processing_mode}")

        # 验证配置一致性
        if set(data_sources) != set(runtime_config.enabled_sources):
            print(f"   ⚠️ 警告: 请求的数据源与启用的数据源不一致")
            print(f"       请求的: {set(data_sources)}")
            print(f"       启用的: {set(runtime_config.enabled_sources)}")

        print("   ✅ 运行时配置组合正常")

    except Exception as e:
        print(f"   ❌ 运行时配置检查失败: {e}")


def check_all_configs():
    """检查所有可用的配置"""
    print("🔍 检查所有可用配置")

    try:
        configs = list_available_configs()

        print(f"📋 可用配置概览:")
        for config_type, names in configs.items():
            print(f"   {config_type}: {', '.join(names)} (共{len(names)}个)")

        print("\n🧪 配置有效性测试:")

        # 测试每个股票列表
        print("   股票列表:")
        for name in configs["stock_lists"]:
            try:
                config = load_stock_list(name)
                print(f"      ✅ {name}: {config.count}个股票")
            except Exception as e:
                print(f"      ❌ {name}: {e}")

        # 测试每个数据源
        print("   数据源:")
        for name in configs["data_sources"]:
            try:
                config = load_data_source(name)
                status = "启用" if config.enabled else "禁用"
                print(f"      ✅ {name}: {status}")
            except Exception as e:
                print(f"      ❌ {name}: {e}")

        # 测试每个场景
        print("   场景:")
        for name in configs["scenarios"]:
            try:
                config = load_scenario(name)
                print(f"      ✅ {name}: {config.processing_mode}模式")
            except Exception as e:
                print(f"      ❌ {name}: {e}")

        # 测试常见配置组合
        print("   常见配置组合:")
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

        print("\n✅ 所有配置检查完成")

    except Exception as e:
        print(f"❌ 配置检查失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="统一的ETL配置检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
    # 检查特定股票列表
    python scripts/config/check_etl_config.py --stock-list f2
    python scripts/config/check_etl_config.py --stock-list v3k --details

    # 检查数据源
    python scripts/config/check_etl_config.py --data-source yfinance --details

    # 检查场景
    python scripts/config/check_etl_config.py --scenario development

    # 检查运行时配置组合
    python scripts/config/check_etl_config.py --runtime f2 yfinance development

    # 检查所有配置
    python scripts/config/check_etl_config.py --all
        """,
    )

    parser.add_argument("--stock-list", help="检查指定的股票列表配置 (f2, m7, n100, v3k)")
    parser.add_argument("--data-source", help="检查指定的数据源配置 (yfinance, sec_edgar)")
    parser.add_argument("--scenario", help="检查指定的场景配置 (development, production)")
    parser.add_argument(
        "--runtime",
        nargs=3,
        metavar=("STOCK_LIST", "DATA_SOURCE", "SCENARIO"),
        help="检查运行时配置组合 (例: f2 yfinance development)",
    )
    parser.add_argument("--all", action="store_true", help="检查所有可用配置")
    parser.add_argument("--details", action="store_true", help="显示详细信息")

    args = parser.parse_args()

    if not any([args.stock_list, args.data_source, args.scenario, args.runtime, args.all]):
        parser.print_help()
        return

    print("🎯 ETL配置检查工具")
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
        print("\n⏹️ 检查被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 检查过程中出现错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
