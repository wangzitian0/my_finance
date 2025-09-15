#!/usr/bin/env python3
"""
集中化ETL配置使用示例
演示如何使用新的etl_loader替代分散的配置读取

Issue #278: ETL配置集中化实现
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def example_old_way():
    """旧的分散配置读取方式 - 不推荐"""
    print("❌ 旧方式 (分散配置读取):")

    # 旧方式: 直接读取配置文件或使用多个不同的配置管理器
    # from common.orthogonal_config import orthogonal_config  # 已废弃
    # import yaml
    # with open('common/config/stock_lists/f2.yml') as f:  # 分散的文件读取
    #     stock_config = yaml.safe_load(f)
    # with open('common/config/data_sources/yfinance.yml') as f:  # 重复的文件操作
    #     source_config = yaml.safe_load(f)

    print("   • 需要知道具体的配置文件路径")
    print("   • 需要手动处理YAML解析和错误")
    print("   • 配置分散在多个目录中")
    print("   • 缺乏统一的验证和缓存")
    print()


def example_new_way():
    """新的集中化配置读取方式 - 推荐"""
    print("✅ 新方式 (集中化ETL配置):")

    try:
        # 导入集中化的ETL配置加载器
        from common.etl_loader import (
            build_etl_config,
            etl_loader,
            list_available_configs,
            load_data_source,
            load_scenario,
            load_stock_list,
        )

        print("   🎯 1. 列出所有可用配置:")
        configs = list_available_configs()
        for config_type, names in configs.items():
            print(f"      {config_type}: {', '.join(names)}")
        print()

        print("   📊 2. 加载单个配置:")
        # 加载股票列表配置
        f2_stocks = load_stock_list("f2")
        print(f"      F2股票列表: {f2_stocks.count}个股票 ({f2_stocks.description})")
        print(f"      股票代码: {', '.join(f2_stocks.tickers)}")

        # 加载数据源配置
        yf_source = load_data_source("yfinance")
        print(f"      YFinance: {yf_source.description}")
        print(f"      支持的数据类型: {', '.join(yf_source.data_types)}")

        # 加载场景配置
        dev_scenario = load_scenario("development")
        print(f"      开发场景: {dev_scenario.processing_mode}模式")
        print(f"      可用数据源: {', '.join(dev_scenario.data_sources)}")
        print()

        print("   🔧 3. 组合运行时配置:")
        # 最强大的功能: 动态组合正交配置
        runtime_config = build_etl_config(
            stock_list="f2", data_sources=["yfinance", "sec_edgar"], scenario="development"
        )

        print(f"      组合标识: {runtime_config.combination}")
        print(f"      股票数量: {runtime_config.ticker_count}")
        print(f"      启用的数据源: {', '.join(runtime_config.enabled_sources)}")
        print(f"      质量阈值: {runtime_config.scenario.quality_thresholds}")
        print()

        print("   🚀 4. 在实际代码中使用:")
        print("      # 获取股票列表进行数据采集")
        print("      tickers = runtime_config.stock_list.tickers")
        print("      # 获取API配置")
        print("      yf_config = runtime_config.data_sources['yfinance'].api_config")
        print("      # 获取处理模式")
        print("      mode = runtime_config.scenario.processing_mode")
        print()

        print("✅ 集中化配置的优势:")
        print("   • 统一的API接口，简单易用")
        print("   • 自动缓存，避免重复读取")
        print("   • 配置验证和错误处理")
        print("   • 支持正交配置组合")
        print("   • 扁平化文件命名，直观易懂")

    except Exception as e:
        print(f"   ❌ 配置加载失败: {e}")
        print("   💡 可能需要先运行配置迁移脚本:")
        print("      python scripts/migrate_etl_config.py --migrate")


def example_usage_in_etl_pipeline():
    """在ETL管道中的实际使用示例"""
    print("\n🔄 ETL管道中的使用示例:")

    try:
        from common.etl_loader import build_etl_config

        # 步骤1: 根据运行环境和需求构建配置
        if "--production" in sys.argv:
            config = build_etl_config("v3k", ["yfinance", "sec_edgar"], "production")
        else:
            config = build_etl_config("f2", ["yfinance"], "development")

        print(f"   📋 配置: {config.combination}")

        # 步骤2: 使用配置进行数据采集
        print("   📈 数据采集:")
        for ticker in config.stock_list.tickers:
            print(f"      处理股票: {ticker}")

            # 对每个启用的数据源进行采集
            for source_name in config.enabled_sources:
                source_config = config.data_sources[source_name]
                rate_limit = source_config.rate_limits.get("requests_per_second", 1)
                print(f"         {source_name}: 限速 {rate_limit} req/s")

        # 步骤3: 应用场景特定的设置
        print("   ⚙️  场景配置:")
        print(f"      处理模式: {config.scenario.processing_mode}")
        print(f"      质量阈值: {config.scenario.quality_thresholds}")
        print(f"      资源限制: {config.scenario.resource_limits}")

        print("\n   ✨ 代码简洁性对比:")
        print("      旧方式: ~50行配置读取和验证代码")
        print("      新方式: 3行配置加载代码")

    except Exception as e:
        print(f"   ❌ 示例运行失败: {e}")


def main():
    print("🎯 ETL配置集中化使用示例\n")
    print("=" * 60)

    example_old_way()
    example_new_way()
    example_usage_in_etl_pipeline()

    print("\n" + "=" * 60)
    print("📚 更多信息:")
    print("   • 查看 common/etl_loader.py 了解完整API")
    print("   • 运行 scripts/migrate_etl_config.py --help 了解迁移选项")
    print("   • 查看 Issue #278 了解设计原理")


if __name__ == "__main__":
    main()
