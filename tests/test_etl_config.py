#!/usr/bin/env python3
"""
ETL配置系统的单元测试
测试集中化配置加载器的各种功能

Issue #278: ETL配置集中化测试
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from common.etl_loader import (
        ETLConfigLoader,
        StockListConfig,
        DataSourceConfig,
        ScenarioConfig,
        RuntimeETLConfig,
        etl_loader,
        load_stock_list,
        load_data_source,
        load_scenario,
        build_etl_config,
        list_available_configs
    )
except ImportError as e:
    print(f"❌ 无法导入ETL配置模块: {e}")
    # 如果导入失败，我们创建一个空的测试类来避免测试运行器失败
    class TestETLConfigImportFailure(unittest.TestCase):
        def test_import_failure(self):
            self.fail(f"ETL配置模块导入失败: {e}")

    if __name__ == '__main__':
        unittest.main()
    else:
        # 这样可以让测试发现机制正常工作
        pass


class TestETLConfigLoader(unittest.TestCase):
    """测试ETLConfigLoader类"""

    def setUp(self):
        """设置测试环境"""
        self.loader = ETLConfigLoader()

    def test_file_mappings(self):
        """测试文件映射配置"""
        mappings = self.loader._stock_list_mapping
        expected_mappings = {
            'f2': 'stock_f2.yml',
            'm7': 'stock_m7.yml',
            'n100': 'stock_n100.yml',
            'v3k': 'stock_v3k.yml'
        }
        self.assertEqual(mappings, expected_mappings)

    def test_list_available_configs(self):
        """测试列出可用配置"""
        configs = self.loader.list_available_configs()

        self.assertIn('stock_lists', configs)
        self.assertIn('data_sources', configs)
        self.assertIn('scenarios', configs)

        self.assertEqual(set(configs['stock_lists']), {'f2', 'm7', 'n100', 'v3k'})
        self.assertEqual(set(configs['data_sources']), {'yfinance', 'sec_edgar'})
        self.assertEqual(set(configs['scenarios']), {'development', 'production'})

    @patch('builtins.open', new_callable=mock_open, read_data="""
description: "Test stock list"
tier: "f2"
max_size_mb: 20
companies:
  MSFT:
    name: "Microsoft Corporation"
    sector: "Technology"
  NVDA:
    name: "NVIDIA Corporation"
    sector: "Technology"
""")
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_stock_list(self, mock_exists, mock_file):
        """测试加载股票列表配置"""
        config = self.loader.load_stock_list('f2')

        self.assertIsInstance(config, StockListConfig)
        self.assertEqual(config.name, 'f2')
        self.assertEqual(config.tier, 'f2')
        self.assertEqual(len(config.tickers), 2)
        self.assertIn('MSFT', config.tickers)
        self.assertIn('NVDA', config.tickers)

    @patch('builtins.open', new_callable=mock_open, read_data="""
description: "Yahoo Finance API"
enabled: true
data_types:
  - "historical_prices"
  - "financial_statements"
api_config:
  base_url: "https://query1.finance.yahoo.com"
  timeout_seconds: 30
rate_limits:
  requests_per_second: 2
output_format:
  file_extension: ".json"
""")
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_data_source(self, mock_exists, mock_file):
        """测试加载数据源配置"""
        config = self.loader.load_data_source('yfinance')

        self.assertIsInstance(config, DataSourceConfig)
        self.assertEqual(config.name, 'yfinance')
        self.assertTrue(config.enabled)
        self.assertIn('historical_prices', config.data_types)

    @patch('builtins.open', new_callable=mock_open, read_data="""
description: "Development environment"
data_sources:
  - "yfinance"
  - "sec_edgar"
processing_mode: "test"
quality_thresholds:
  min_success_rate: 0.8
resource_limits:
  max_concurrent_requests: 5
optimizations:
  cache_enabled: true
""")
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_scenario(self, mock_exists, mock_file):
        """测试加载场景配置"""
        config = self.loader.load_scenario('development')

        self.assertIsInstance(config, ScenarioConfig)
        self.assertEqual(config.name, 'development')
        self.assertEqual(config.processing_mode, 'test')
        self.assertIn('yfinance', config.data_sources)

    def test_invalid_config_names(self):
        """测试无效的配置名称"""
        with self.assertRaises(ValueError):
            self.loader.load_stock_list('invalid')

        with self.assertRaises(ValueError):
            self.loader.load_data_source('invalid')

        with self.assertRaises(ValueError):
            self.loader.load_scenario('invalid')

    def test_cache_functionality(self):
        """测试缓存功能"""
        # 清除缓存
        self.loader.clear_cache()
        self.assertEqual(len(self.loader._cache), 0)

    def test_legacy_config_mapping(self):
        """测试旧配置文件映射"""
        mapping = self.loader.get_legacy_config_mapping()

        # 检查映射包含所有预期的文件
        self.assertIn('common/config/stock_lists/f2.yml', mapping)
        self.assertIn('common/config/etl/stock_f2.yml', mapping.values())


class TestRuntimeConfigBuilding(unittest.TestCase):
    """测试运行时配置构建"""

    def setUp(self):
        """设置测试环境"""
        # Mock配置数据
        self.mock_stock_config = """
description: "2-company subset"
tier: "f2"
max_size_mb: 20
companies:
  MSFT:
    name: "Microsoft Corporation"
    sector: "Technology"
  NVDA:
    name: "NVIDIA Corporation"
    sector: "Technology"
"""

        self.mock_yf_config = """
description: "Yahoo Finance API"
enabled: true
data_types:
  - "historical_prices"
api_config:
  base_url: "https://query1.finance.yahoo.com"
rate_limits:
  requests_per_second: 2
output_format:
  file_extension: ".json"
"""

        self.mock_scenario_config = """
description: "Development environment"
data_sources:
  - "yfinance"
  - "sec_edgar"
processing_mode: "test"
quality_thresholds:
  min_success_rate: 0.8
resource_limits:
  max_concurrent_requests: 5
optimizations:
  cache_enabled: true
"""

    @patch('pathlib.Path.exists', return_value=True)
    def test_build_runtime_config(self, mock_exists):
        """测试构建运行时配置"""
        with patch('builtins.open', mock_open()) as mock_file:
            # 设置不同文件的内容
            mock_file.side_effect = [
                mock_open(read_data=self.mock_stock_config).return_value,
                mock_open(read_data=self.mock_yf_config).return_value,
                mock_open(read_data=self.mock_scenario_config).return_value
            ]

            loader = ETLConfigLoader()
            config = loader.build_runtime_config('f2', ['yfinance'], 'development')

            self.assertIsInstance(config, RuntimeETLConfig)
            self.assertEqual(config.combination, 'f2_yfinance_development')
            self.assertEqual(config.ticker_count, 2)
            self.assertIn('yfinance', config.enabled_sources)

    @patch('pathlib.Path.exists', return_value=True)
    def test_invalid_data_source_in_scenario(self, mock_exists):
        """测试场景中不可用的数据源"""
        # 修改scenario配置，只允许yfinance
        limited_scenario = """
description: "Limited environment"
data_sources:
  - "yfinance"
processing_mode: "test"
"""

        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = [
                mock_open(read_data=self.mock_stock_config).return_value,
                mock_open(read_data=self.mock_yf_config).return_value,
                mock_open(read_data=limited_scenario).return_value
            ]

            loader = ETLConfigLoader()

            # 尝试使用不可用的数据源应该抛出错误
            with self.assertRaises(ValueError):
                loader.build_runtime_config('f2', ['yfinance', 'sec_edgar'], 'development')


class TestConvenienceFunctions(unittest.TestCase):
    """测试便捷函数"""

    @patch('common.etl_loader.etl_loader')
    def test_convenience_functions(self, mock_loader):
        """测试便捷函数调用"""
        # Mock返回值
        mock_config = StockListConfig('f2', 'test', ['MSFT'], {}, 'f2', 20)
        mock_loader.load_stock_list.return_value = mock_config

        # 测试便捷函数
        result = load_stock_list('f2')

        # 验证调用
        mock_loader.load_stock_list.assert_called_once_with('f2')
        self.assertEqual(result, mock_config)


class TestConfigValidation(unittest.TestCase):
    """测试配置验证"""

    def setUp(self):
        """设置测试环境"""
        self.loader = ETLConfigLoader()

    @patch('pathlib.Path.exists', return_value=False)
    def test_missing_config_files(self, mock_exists):
        """测试缺失配置文件的情况"""
        errors = self.loader.validate_config_files()

        # 应该为每个配置类型返回错误
        self.assertTrue(len(errors) > 0)

    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', mock_open(read_data="invalid: yaml: content: ["))
    def test_invalid_yaml_format(self, mock_exists):
        """测试无效的YAML格式"""
        with self.assertRaises(ValueError):
            self.loader._load_yaml(Path('test.yml'))


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_list_available_configs_function(self):
        """测试list_available_configs函数"""
        configs = list_available_configs()

        self.assertIsInstance(configs, dict)
        self.assertIn('stock_lists', configs)
        self.assertIn('data_sources', configs)
        self.assertIn('scenarios', configs)

    @patch('pathlib.Path.exists', return_value=True)
    def test_full_workflow_mock(self, mock_exists):
        """测试完整的配置加载工作流程（模拟）"""
        mock_configs = {
            'stock_f2.yml': """
description: "F2 stocks"
tier: "f2"
companies:
  MSFT:
    name: "Microsoft Corporation"
""",
            'source_yfinance.yml': """
description: "Yahoo Finance"
enabled: true
data_types: ["historical_prices"]
api_config: {}
rate_limits: {}
output_format: {}
""",
            'scenario_dev.yml': """
description: "Development"
data_sources: ["yfinance"]
processing_mode: "test"
quality_thresholds: {}
resource_limits: {}
optimizations: {}
"""
        }

        def mock_open_func(file_path, *args, **kwargs):
            filename = file_path.name
            if filename in mock_configs:
                return mock_open(read_data=mock_configs[filename]).return_value
            raise FileNotFoundError()

        with patch('builtins.open', side_effect=mock_open_func):
            config = build_etl_config('f2', ['yfinance'], 'development')

            self.assertIsInstance(config, RuntimeETLConfig)
            self.assertEqual(config.combination, 'f2_yfinance_development')


if __name__ == '__main__':
    unittest.main(verbosity=2)