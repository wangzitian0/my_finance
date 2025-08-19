#!/usr/bin/env python3
"""
Unit tests for multi-model DCF configuration isomorphism.

Tests that:
1. F2 build works with DeepSeek model
2. Configuration is isomorphic across different LLM models
3. Build and fast-build work identically except LLM choice
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import yaml

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestMultiModelDCF(unittest.TestCase):
    """Test multi-model DCF configuration compatibility"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(__file__).parent.parent
        self.config_dir = self.test_dir / "data" / "llm" / "configs"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def test_deepseek_config_exists(self):
        """Test that DeepSeek fast configuration exists and is valid"""
        deepseek_config_path = self.config_dir / "deepseek_fast.yml"
        
        self.assertTrue(
            deepseek_config_path.exists(),
            f"DeepSeek config not found at {deepseek_config_path}"
        )
        
        with open(deepseek_config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required top-level sections
        required_sections = ['llm_service', 'generation', 'dcf_generation']
        for section in required_sections:
            self.assertIn(section, config, f"Missing required section: {section}")
        
        # Validate LLM service fields
        llm_service = config['llm_service']
        self.assertEqual(llm_service['model'], 'deepseek-r1:1.5b')
        self.assertEqual(llm_service['provider'], 'ollama')
        self.assertLessEqual(llm_service['timeout'], 60, "Fast mode should have short timeout")
        
        # Validate fast mode is enabled
        dcf_generation = config['dcf_generation']
        self.assertTrue(dcf_generation.get('fast_mode', False))

    def test_default_config_exists(self):
        """Test that default (non-fast) configuration exists"""
        # Check for existing LLM configs
        config_files = list(self.config_dir.glob("*.yml"))
        config_files = [f for f in config_files if not f.name.startswith('deepseek')]
        
        # Include default config if it exists
        default_config_path = self.config_dir / "default.yml"
        if default_config_path.exists():
            config_files.append(default_config_path)
        
        self.assertGreater(len(config_files), 0, "No default LLM config found")

    def test_config_isomorphism(self):
        """Test that all LLM configs have the same structure (isomorphic)"""
        config_files = list(self.config_dir.glob("*.yml"))
        self.assertGreater(len(config_files), 1, "Need at least 2 configs to test isomorphism")
        
        configs = {}
        for config_file in config_files:
            with open(config_file, 'r') as f:
                configs[config_file.name] = yaml.safe_load(f)
        
        # Get the structure of the first config
        first_config_name = list(configs.keys())[0]
        first_config = configs[first_config_name]
        expected_keys = set(first_config.keys())
        
        # Verify all configs have the same structure
        for config_name, config in configs.items():
            config_keys = set(config.keys())
            missing_keys = expected_keys - config_keys
            extra_keys = config_keys - expected_keys
            
            self.assertEqual(
                len(missing_keys), 0,
                f"Config {config_name} missing keys: {missing_keys}"
            )
            self.assertEqual(
                len(extra_keys), 0,
                f"Config {config_name} has extra keys: {extra_keys}"
            )

    @patch('dcf_engine.llm_dcf_generator.LLMDCFGenerator')
    def test_f2_build_with_deepseek(self, mock_llm_dcf):
        """Test that F2 build works with DeepSeek model"""
        # Mock the LLM DCF generator to avoid actual LLM calls
        mock_instance = MagicMock()
        mock_instance.generate_comprehensive_dcf_report.return_value = {
            'ticker': 'AAPL',
            'dcf_valuation': 150.0,
            'model_used': 'deepseek-r1:1.5b',
            'timestamp': '2025-08-19T19:30:00Z'
        }
        mock_llm_dcf.return_value = mock_instance
        
        # Set environment variables for fast mode
        with patch.dict(os.environ, {
            'DCF_FAST_MODE': 'true',
            'DCF_CONFIG_PATH': str(self.config_dir / 'deepseek_fast.yml')
        }):
            # Import and test the build system
            try:
                from ETL.build_dataset import build_dataset
                
                # Test F2 build with DeepSeek
                success = build_dataset('f2')
                
                # Verify the build completed
                self.assertTrue(success, "F2 build with DeepSeek should succeed")
                
                # Verify the LLM generator was called with fast mode
                mock_llm_dcf.assert_called()
                call_args = mock_llm_dcf.call_args
                
                # Check if fast_mode was passed
                if call_args and len(call_args) > 1:
                    kwargs = call_args[1]
                    self.assertTrue(
                        kwargs.get('fast_mode', False),
                        "DeepSeek build should use fast_mode=True"
                    )
                
            except ImportError as e:
                self.skipTest(f"Build system not available: {e}")

    def test_build_vs_fast_build_config_difference(self):
        """Test that build and fast-build only differ in LLM configuration"""
        # Load both configs
        deepseek_config_path = self.config_dir / "deepseek_fast.yml"
        
        if not deepseek_config_path.exists():
            self.skipTest("DeepSeek config not found")
        
        with open(deepseek_config_path, 'r') as f:
            deepseek_config = yaml.safe_load(f)
        
        # Find a default config for comparison
        other_configs = [f for f in self.config_dir.glob("*.yml") 
                        if not f.name.startswith('deepseek')]
        
        if not other_configs:
            self.skipTest("No default config found for comparison")
        
        with open(other_configs[0], 'r') as f:
            default_config = yaml.safe_load(f)
        
        # Compare configurations - only LLM-specific fields should differ
        llm_specific_fields = {'model', 'temperature', 'max_tokens', 'timeout', 'fast_mode'}
        infrastructure_fields = {'base_url'}  # Should be the same
        
        # Infrastructure should be identical (check nested structure)
        if 'llm_service' in deepseek_config and 'llm_service' in default_config:
            for field in infrastructure_fields:
                deepseek_value = deepseek_config['llm_service'].get(field)
                default_value = default_config['llm_service'].get(field)
                self.assertEqual(
                    deepseek_value,
                    default_value,
                    f"Infrastructure field {field} should be identical"
                )
        
        # Check that models are different
        deepseek_model = deepseek_config['llm_service']['model']
        default_model = default_config['llm_service']['model']
        
        self.assertNotEqual(
            deepseek_model, 
            default_model, 
            "Models should be different between configs"
        )
        
        # Check that fast_mode differs
        deepseek_fast = deepseek_config['dcf_generation'].get('fast_mode', False)
        default_fast = default_config['dcf_generation'].get('fast_mode', False)
        
        self.assertTrue(deepseek_fast, "DeepSeek should have fast_mode=True")
        self.assertFalse(default_fast, "Default should have fast_mode=False")

    def test_p3_script_fast_build_command(self):
        """Test that p3 script has fast-build command"""
        p3_script_path = self.test_dir / "p3"
        
        self.assertTrue(p3_script_path.exists(), "p3 script not found")
        
        with open(p3_script_path, 'r') as f:
            script_content = f.read()
        
        # Check for fast-build command
        self.assertIn('cmd_fast_build', script_content, "fast-build command not found in p3 script")
        self.assertIn('deepseek-r1:1.5b', script_content, "DeepSeek model not referenced in p3 script")
        self.assertIn('DCF_FAST_MODE', script_content, "Fast mode environment variable not set")

    def test_environment_variable_configuration(self):
        """Test that environment variables properly control LLM selection"""
        from dcf_engine.llm_dcf_generator import LLMDCFGenerator
        
        # Test default behavior (no environment variables)
        with patch.dict(os.environ, {}, clear=True):
            # Remove DCF environment variables if they exist
            for key in list(os.environ.keys()):
                if key.startswith('DCF_'):
                    os.environ.pop(key, None)
            
            generator = LLMDCFGenerator()
            # Should use default config or create with default settings
            self.assertIsNotNone(generator)
        
        # Test fast mode behavior
        with patch.dict(os.environ, {
            'DCF_FAST_MODE': 'true',
            'DCF_CONFIG_PATH': str(self.config_dir / 'deepseek_fast.yml')
        }):
            if (self.config_dir / 'deepseek_fast.yml').exists():
                generator = LLMDCFGenerator(fast_mode=True)
                self.assertIsNotNone(generator)
            else:
                self.skipTest("DeepSeek config not available")


if __name__ == '__main__':
    unittest.main()