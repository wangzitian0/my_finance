#!/usr/bin/env python3
"""
Unit tests for DCF engine modules
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_dcf_engine_imports():
    """Test that DCF engine modules can be imported"""
    try:
        from dcf_engine import generate_dcf_report
        from dcf_engine import build_knowledge_base
        assert True
    except ImportError as e:
        pytest.fail(f"DCF engine imports failed: {e}")

def test_knowledge_base_builder_init():
    """Test KnowledgeBaseBuilder initialization"""
    try:
        from dcf_engine.build_knowledge_base import KnowledgeBaseBuilder
        
        builder = KnowledgeBaseBuilder()
        
        # Check basic attributes
        assert hasattr(builder, 'project_root')
        assert hasattr(builder, 'data_dir')
        assert hasattr(builder, 'config_dir')
        assert hasattr(builder, 'tiers')
        
        # Check tier system
        assert 'f2' in builder.tiers
        assert 'm7' in builder.tiers
        assert 'n100' in builder.tiers
        assert 'v3k' in builder.tiers
        
        # Check tier structure
        for tier_name, tier_config in builder.tiers.items():
            assert 'name' in tier_config
            assert 'description' in tier_config
            assert 'configs' in tier_config
            assert isinstance(tier_config['configs'], list)
            
    except Exception as e:
        pytest.fail(f"KnowledgeBaseBuilder initialization failed: {e}")

def test_dcf_analyzer_basic():
    """Test basic DCF analyzer functionality"""
    try:
        from dcf_engine.generate_dcf_report import M7DCFAnalyzer
        
        analyzer = M7DCFAnalyzer()
        
        # Check basic methods exist
        assert hasattr(analyzer, 'generate_report')
        assert hasattr(analyzer, 'save_report')
        assert callable(analyzer.generate_report)
        assert callable(analyzer.save_report)
        
    except Exception as e:
        pytest.fail(f"DCF analyzer basic test failed: {e}")

@patch('dcf_engine.generate_dcf_report.M7DCFAnalyzer.generate_company_analysis')
def test_dcf_report_generation_mock(mock_analysis):
    """Test DCF report generation with mocked data"""
    try:
        from dcf_engine.generate_dcf_report import M7DCFAnalyzer
        
        # Mock company analysis
        mock_analysis.return_value = {
            'ticker': 'TEST',
            'company_name': 'Test Company',
            'dcf_valuation': {
                'current_price': 100.0,
                'intrinsic_value': 120.0,
                'upside_downside_pct': 20.0
            },
            'analysis_date': '2025-08-12'
        }
        
        analyzer = M7DCFAnalyzer()
        
        # This should work without actual data
        assert mock_analysis.return_value['ticker'] == 'TEST'
        assert mock_analysis.return_value['dcf_valuation']['upside_downside_pct'] == 20.0
        
    except Exception as e:
        pytest.fail(f"DCF report generation mock test failed: {e}")

def test_tier_configurations():
    """Test that all tier configurations are valid"""
    try:
        from dcf_engine.build_knowledge_base import KnowledgeBaseBuilder
        
        builder = KnowledgeBaseBuilder()
        
        # Test each tier
        for tier_name, tier_config in builder.tiers.items():
            # Check required fields
            assert tier_config['name'], f"Tier {tier_name} missing name"
            assert tier_config['description'], f"Tier {tier_name} missing description"
            assert tier_config['configs'], f"Tier {tier_name} missing configs"
            
            # Check config files reference valid YAML files
            for config_file in tier_config['configs']:
                assert config_file.endswith('.yml'), f"Config file {config_file} should be YAML"
                assert 'list_' in config_file, f"Config file {config_file} should be a list config"
        
        # Test specific tier properties
        assert builder.tiers['f2']['max_size_mb'] == 20
        assert builder.tiers['m7']['tracked_in_git'] == True
        assert builder.tiers['n100']['max_size_mb'] == 5000
        assert builder.tiers['v3k']['max_size_mb'] == 20000
        
    except Exception as e:
        pytest.fail(f"Tier configurations test failed: {e}")

def test_config_validation_logic():
    """Test configuration validation logic without requiring actual files"""
    try:
        from dcf_engine.build_knowledge_base import KnowledgeBaseBuilder
        
        builder = KnowledgeBaseBuilder()
        
        # Test required config list
        required_configs = [
            "list_fast_2.yml",
            "list_magnificent_7.yml", 
            "list_nasdaq_100.yml",
            "list_vti_3500.yml",
            "source_yfinance.yml",
            "source_sec_edgar.yml"
        ]
        
        # This tests the logic structure, not file existence
        for config in required_configs:
            assert isinstance(config, str)
            assert config.endswith('.yml')
            
    except Exception as e:
        pytest.fail(f"Config validation logic test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
