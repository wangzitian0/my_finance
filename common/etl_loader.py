#!/usr/bin/env python3
"""
集中化 ETL 配置加载器
统一管理所有 ETL 配置的读取，支持三个正交维度：Stock Lists × Data Sources × Scenarios

设计原则：
- 集中化：所有ETL配置通过此模块读取
- 正交性：三个维度独立配置，运行时动态组合
- 简洁性：扁平化命名，直观易懂
- 缓存：避免重复读取，提高性能
- 验证：配置有效性检查和错误处理
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

# Add common to path
sys.path.insert(0, str(Path(__file__).parent))
from core.directory_manager import directory_manager


@dataclass
class StockListConfig:
    """Stock List配置"""

    name: str
    description: str
    tickers: List[str]
    companies: Dict[str, Dict[str, str]]  # ticker -> {name, cik, sector, ...}
    tier: str  # f2, m7, n100, v3k
    max_size_mb: int

    @property
    def count(self) -> int:
        return len(self.tickers)


@dataclass
class DataSourceConfig:
    """Data Source配置"""

    name: str
    description: str
    enabled: bool
    api_config: Dict[str, Any]
    rate_limits: Dict[str, Any]
    data_types: List[str]
    output_format: Dict[str, Any]


@dataclass
class ScenarioConfig:
    """Scenario配置"""

    name: str
    description: str
    data_sources: List[str]  # 可用的数据源列表
    processing_mode: str  # 'full', 'incremental', 'test'
    output_formats: List[str]
    quality_thresholds: Dict[str, float]
    resource_limits: Dict[str, Any]
    optimizations: Dict[str, Any]


@dataclass
class RuntimeETLConfig:
    """运行时组合的ETL配置"""

    stock_list: StockListConfig
    data_sources: Dict[str, DataSourceConfig]  # name -> config
    scenario: ScenarioConfig

    # 运行时信息
    combination: str  # f2_yfinance+sec_edgar_development
    generated_at: str

    @property
    def ticker_count(self) -> int:
        return self.stock_list.count

    @property
    def enabled_sources(self) -> List[str]:
        return [name for name, config in self.data_sources.items() if config.enabled]


class ETLConfigLoader:
    """集中化的ETL配置加载器"""

    def __init__(self):
        self.directory_manager = directory_manager
        self.config_root = self.directory_manager.get_config_path()
        self.etl_config_dir = self.config_root / "etl"

        # 确保配置目录存在
        self.etl_config_dir.mkdir(exist_ok=True)

        # 配置缓存
        self._cache = {}

        # 映射旧的配置名到新的文件名
        self._stock_list_mapping = {
            "f2": "stock_f2.yml",
            "m7": "stock_m7.yml",
            "n100": "stock_n100.yml",
            "v3k": "stock_v3k.yml",
        }

        self._data_source_mapping = {
            "yfinance": "source_yfinance.yml",
            "sec_edgar": "source_sec_edgar.yml",
        }

        self._scenario_mapping = {
            "development": "scenario_dev.yml",
            "production": "scenario_prod.yml",
        }

    def list_available_configs(self) -> Dict[str, List[str]]:
        """列出所有可用的配置"""
        return {
            "stock_lists": list(self._stock_list_mapping.keys()),
            "data_sources": list(self._data_source_mapping.keys()),
            "scenarios": list(self._scenario_mapping.keys()),
        }

    def load_stock_list(self, name: str) -> StockListConfig:
        """加载股票列表配置"""
        cache_key = f"stock_{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if name not in self._stock_list_mapping:
            raise ValueError(
                f"未知的股票列表: {name}. 可用的: {list(self._stock_list_mapping.keys())}"
            )

        file_path = self.etl_config_dir / self._stock_list_mapping[name]
        config_data = self._load_yaml(file_path)

        # 解析公司信息，生成tickers列表
        companies = config_data.get("companies", {})
        tickers = list(companies.keys())

        config = StockListConfig(
            name=name,
            description=config_data.get("description", ""),
            tickers=tickers,
            companies=companies,
            tier=config_data.get("tier", name),
            max_size_mb=config_data.get("max_size_mb", 100),
        )

        self._cache[cache_key] = config
        return config

    def load_data_source(self, name: str) -> DataSourceConfig:
        """加载数据源配置"""
        cache_key = f"source_{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if name not in self._data_source_mapping:
            raise ValueError(
                f"未知的数据源: {name}. 可用的: {list(self._data_source_mapping.keys())}"
            )

        file_path = self.etl_config_dir / self._data_source_mapping[name]
        config_data = self._load_yaml(file_path)

        config = DataSourceConfig(
            name=name,
            description=config_data.get("description", ""),
            enabled=config_data.get("enabled", True),
            api_config=config_data.get("api_config", {}),
            rate_limits=config_data.get("rate_limits", {}),
            data_types=config_data.get("data_types", []),
            output_format=config_data.get("output_format", {}),
        )

        self._cache[cache_key] = config
        return config

    def load_scenario(self, name: str) -> ScenarioConfig:
        """加载场景配置"""
        cache_key = f"scenario_{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if name not in self._scenario_mapping:
            raise ValueError(f"未知的场景: {name}. 可用的: {list(self._scenario_mapping.keys())}")

        file_path = self.etl_config_dir / self._scenario_mapping[name]
        config_data = self._load_yaml(file_path)

        config = ScenarioConfig(
            name=name,
            description=config_data.get("description", ""),
            data_sources=config_data.get("data_sources", []),
            processing_mode=config_data.get("processing_mode", "full"),
            output_formats=config_data.get("output_formats", ["json"]),
            quality_thresholds=config_data.get("quality_thresholds", {}),
            resource_limits=config_data.get("resource_limits", {}),
            optimizations=config_data.get("optimizations", {}),
        )

        self._cache[cache_key] = config
        return config

    def build_runtime_config(
        self, stock_list: str, data_sources: List[str], scenario: str
    ) -> RuntimeETLConfig:
        """
        组合正交配置生成运行时配置

        Args:
            stock_list: 股票列表名 (f2, m7, n100, v3k)
            data_sources: 数据源列表 ['yfinance', 'sec_edgar']
            scenario: 场景名 ('development', 'production')

        Returns:
            运行时ETL配置
        """
        # 加载各个维度的配置
        stocks = self.load_stock_list(stock_list)
        sources = {name: self.load_data_source(name) for name in data_sources}
        scene = self.load_scenario(scenario)

        # 验证数据源在场景中可用
        available_sources = set(scene.data_sources)
        requested_sources = set(data_sources)
        if not requested_sources.issubset(available_sources):
            missing = requested_sources - available_sources
            raise ValueError(
                f"数据源 {missing} 在场景 '{scenario}' 中不可用. 可用的: {available_sources}"
            )

        # 生成组合标识
        combination = f"{stock_list}_{'+'.join(data_sources)}_{scenario}"

        return RuntimeETLConfig(
            stock_list=stocks,
            data_sources=sources,
            scenario=scene,
            combination=combination,
            generated_at="runtime",
        )

    def get_legacy_config_mapping(self) -> Dict[str, str]:
        """获取新旧配置文件的映射关系，用于迁移"""
        return {
            # Stock Lists
            "common/config/stock_lists/f2.yml": "common/config/etl/stock_f2.yml",
            "common/config/stock_lists/m7.yml": "common/config/etl/stock_m7.yml",
            "common/config/stock_lists/n100.yml": "common/config/etl/stock_n100.yml",
            "common/config/stock_lists/v3k.yml": "common/config/etl/stock_v3k.yml",
            # Data Sources
            "common/config/data_sources/yfinance.yml": "common/config/etl/source_yfinance.yml",
            "common/config/data_sources/sec_edgar.yml": "common/config/etl/source_sec_edgar.yml",
            # Scenarios
            "common/config/scenarios/development.yml": "common/config/etl/scenario_dev.yml",
            "common/config/scenarios/production.yml": "common/config/etl/scenario_prod.yml",
        }

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """加载YAML文件"""
        if not file_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"YAML解析错误 {file_path}: {e}")
        except Exception as e:
            raise ValueError(f"配置文件读取错误 {file_path}: {e}")

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()

    def validate_config_files(self) -> List[str]:
        """验证所有配置文件是否存在和格式正确"""
        errors = []

        all_files = {}
        all_files.update({k: self.etl_config_dir / v for k, v in self._stock_list_mapping.items()})
        all_files.update({k: self.etl_config_dir / v for k, v in self._data_source_mapping.items()})
        all_files.update({k: self.etl_config_dir / v for k, v in self._scenario_mapping.items()})

        for name, file_path in all_files.items():
            try:
                self._load_yaml(file_path)
            except Exception as e:
                errors.append(f"{name}: {e}")

        return errors


# 全局实例
etl_loader = ETLConfigLoader()


# 便捷函数
def load_stock_list(name: str) -> StockListConfig:
    """加载股票列表配置"""
    return etl_loader.load_stock_list(name)


def load_data_source(name: str) -> DataSourceConfig:
    """加载数据源配置"""
    return etl_loader.load_data_source(name)


def load_scenario(name: str) -> ScenarioConfig:
    """加载场景配置"""
    return etl_loader.load_scenario(name)


def build_etl_config(stock_list: str, data_sources: List[str], scenario: str) -> RuntimeETLConfig:
    """构建运行时ETL配置"""
    return etl_loader.build_runtime_config(stock_list, data_sources, scenario)


def list_available_configs() -> Dict[str, List[str]]:
    """列出所有可用的配置"""
    return etl_loader.list_available_configs()
