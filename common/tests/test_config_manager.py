#!/usr/bin/env python3
"""
Test suite for the unified config manager system.
Tests configuration loading, validation, and management.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from common.config_manager import (
    ConfigManager,
    ConfigSchema,
    ConfigType,
    get_company_list,
    get_config,
    get_data_source_config,
    get_llm_config,
)


class TestConfigSchema:
    """Test ConfigSchema dataclass"""

    def test_config_schema_creation(self):
        """Test ConfigSchema creation"""
        schema = ConfigSchema(
            name="test_config",
            path="test.yml",
            required=True,
            format="yaml",
            description="Test configuration",
        )

        assert schema.name == "test_config"
        assert schema.path == "test.yml"
        assert schema.required is True
        assert schema.format == "yaml"
        assert schema.description == "Test configuration"

    def test_config_schema_defaults(self):
        """Test ConfigSchema default values"""
        schema = ConfigSchema(name="test", path="test.yml")

        assert schema.required is True
        assert schema.format == "yaml"
        assert schema.description == ""


class TestConfigManager:
    """Test ConfigManager class"""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory for testing"""
        temp_dir = tempfile.mkdtemp()
        config_dir = Path(temp_dir)

        # Create sample config files
        sample_configs = {
            "directory_structure.yml": {
                "storage": {"backend": "local_filesystem", "root_path": "build_data"},
                "layers": {
                    "stage_00_raw": {
                        "description": "Raw data layer",
                        "subdirs": ["sec-edgar", "yfinance"],
                    }
                },
            },
            "list_magnificent_7.yml": {
                "companies": [
                    {"ticker": "AAPL", "name": "Apple Inc.", "cik": "0000320193"},
                    {"ticker": "MSFT", "name": "Microsoft Corporation", "cik": "0000789019"},
                ]
            },
            "stage_00_original_sec_edgar.yml": {
                "source": "sec_edgar",
                "description": "SEC Edgar data source",
                "endpoints": {
                    "filings": "https://data.sec.gov/submissions/",
                    "facts": "https://data.sec.gov/api/xbrl/companyfacts/",
                },
            },
        }

        # Create LLM config directory
        llm_config_dir = config_dir / "llm" / "configs"
        llm_config_dir.mkdir(parents=True, exist_ok=True)

        llm_configs = {
            "default.yml": {"model": "gpt-3.5-turbo", "temperature": 0.1, "max_tokens": 2000},
            "deepseek_fast.yml": {"model": "deepseek-chat", "temperature": 0.0, "max_tokens": 1000},
        }

        # Write config files
        for filename, content in sample_configs.items():
            with open(config_dir / filename, "w") as f:
                yaml.dump(content, f)

        for filename, content in llm_configs.items():
            with open(llm_config_dir / filename, "w") as f:
                yaml.dump(content, f)

        yield config_dir

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """Create ConfigManager instance for testing"""
        return ConfigManager(config_root=temp_config_dir)

    def test_initialization(self, config_manager, temp_config_dir):
        """Test ConfigManager initialization"""
        assert config_manager.config_root == temp_config_dir
        assert config_manager._cache is not None
        assert config_manager._schemas is not None

        # Check that configs are loaded
        assert "directory_structure" in config_manager._cache
        assert "magnificent_7" in config_manager._cache
        assert "llm_configs" in config_manager._cache

    def test_schema_definition(self, config_manager):
        """Test configuration schema definition"""
        schemas = config_manager._schemas

        # Check required schemas exist
        required_schemas = [
            "directory_structure",
            "magnificent_7",
            "nasdaq_100",
            "fast_2",
            "vti_3500",
            "sec_edgar_nasdaq100",
            "stage_00_original_sec_edgar",
            "stage_00_original_yfinance",
        ]

        for schema_name in required_schemas:
            assert schema_name in schemas
            schema = schemas[schema_name]
            assert isinstance(schema, ConfigSchema)
            assert schema.name == schema_name
            assert schema.path.endswith(".yml")

    def test_get_config(self, config_manager):
        """Test get_config method"""
        # Test existing config
        dir_config = config_manager.get_config("directory_structure")
        assert "storage" in dir_config
        assert "layers" in dir_config

        # Test non-existent config
        empty_config = config_manager.get_config("nonexistent")
        assert empty_config == {}

        # Test reload functionality
        original_config = config_manager.get_config("directory_structure")
        reloaded_config = config_manager.get_config("directory_structure", reload=True)
        assert original_config == reloaded_config

    def test_get_company_list(self, config_manager):
        """Test get_company_list method"""
        companies = config_manager.get_company_list("magnificent_7")

        assert len(companies) == 2
        assert companies[0]["ticker"] == "AAPL"
        assert companies[0]["name"] == "Apple Inc."
        assert companies[0]["cik"] == "0000320193"
        assert companies[1]["ticker"] == "MSFT"

        # Test non-existent list
        empty_list = config_manager.get_company_list("nonexistent")
        assert empty_list == []

    def test_get_llm_config(self, config_manager):
        """Test get_llm_config method"""
        # Test default config
        default_config = config_manager.get_llm_config("default")
        assert default_config["model"] == "gpt-3.5-turbo"
        assert default_config["temperature"] == 0.1

        # Test specific config
        deepseek_config = config_manager.get_llm_config("deepseek_fast")
        assert deepseek_config["model"] == "deepseek-chat"
        assert deepseek_config["temperature"] == 0.0

        # Test non-existent config
        empty_config = config_manager.get_llm_config("nonexistent")
        assert empty_config == {}

    def test_get_data_source_config(self, config_manager):
        """Test get_data_source_config method"""
        sec_config = config_manager.get_data_source_config("sec_edgar")

        assert sec_config["source"] == "sec_edgar"
        assert "endpoints" in sec_config
        assert "filings" in sec_config["endpoints"]

        # Test non-existent source
        empty_config = config_manager.get_data_source_config("nonexistent")
        assert empty_config == {}

    def test_get_directory_config(self, config_manager):
        """Test get_directory_config method"""
        dir_config = config_manager.get_directory_config()

        assert "storage" in dir_config
        assert "layers" in dir_config
        assert dir_config["storage"]["backend"] == "local_filesystem"

    def test_list_available_configs(self, config_manager):
        """Test list_available_configs method"""
        available_configs = config_manager.list_available_configs()

        # Check required configs are listed
        assert "directory_structure" in available_configs
        assert "magnificent_7" in available_configs
        assert "llm_configs" in available_configs

        # Should be a reasonable number of configs
        assert len(available_configs) > 5

    def test_validate_config(self, config_manager):
        """Test validate_config method"""
        # Test valid config
        assert config_manager.validate_config("directory_structure") is True
        assert config_manager.validate_config("magnificent_7") is True

        # Test invalid/non-existent config
        assert config_manager.validate_config("nonexistent") is False

    def test_get_config_path(self, config_manager, temp_config_dir):
        """Test get_config_path method"""
        # Test existing config
        config_path = config_manager.get_config_path("directory_structure")
        assert config_path == temp_config_dir / "directory_structure.yml"
        assert config_path.exists()

        # Test non-existent config
        invalid_path = config_manager.get_config_path("nonexistent")
        assert invalid_path is None

    def test_reload_all(self, config_manager, temp_config_dir):
        """Test reload_all method"""
        # Modify cache
        config_manager._cache["test_key"] = "test_value"
        assert "test_key" in config_manager._cache

        # Reload all configs
        config_manager.reload_all()

        # Test key should be gone
        assert "test_key" not in config_manager._cache

        # But original configs should still be there
        assert "directory_structure" in config_manager._cache
        assert "magnificent_7" in config_manager._cache

    def test_create_config_template(self, config_manager, temp_config_dir):
        """Test create_config_template method"""
        template_data = {"test_config": {"setting1": "value1", "setting2": "value2"}}

        # Add schema for test config
        config_manager._schemas["test_template"] = ConfigSchema(
            name="test_template", path="test_template.yml"
        )

        # Create template
        result = config_manager.create_config_template("test_template", template_data)
        assert result is True

        # Check file was created
        template_path = temp_config_dir / "test_template.yml"
        assert template_path.exists()

        # Check content
        with open(template_path) as f:
            loaded_data = yaml.safe_load(f)
        assert loaded_data == template_data

    def test_update_config(self, config_manager, temp_config_dir):
        """Test update_config method"""
        # Test merge update
        updates = {"storage": {"backend": "aws_s3", "new_setting": "test_value"}}

        result = config_manager.update_config("directory_structure", updates, merge=True)
        assert result is True

        # Check merge worked
        updated_config = config_manager.get_config("directory_structure")
        assert updated_config["storage"]["backend"] == "aws_s3"
        assert updated_config["storage"]["new_setting"] == "test_value"
        assert "layers" in updated_config  # Original data preserved

        # Test replace update
        replacement_data = {"completely_new": "data"}
        result = config_manager.update_config("directory_structure", replacement_data, merge=False)
        assert result is True

        # Check replacement worked
        replaced_config = config_manager.get_config("directory_structure")
        assert replaced_config == replacement_data
        assert "layers" not in replaced_config  # Original data gone


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_get_config_function(self):
        """Test get_config convenience function"""
        with patch("common.config_manager.config_manager") as mock_cm:
            mock_cm.get_config.return_value = {"test": "data"}

            result = get_config("test_config")
            assert result == {"test": "data"}
            mock_cm.get_config.assert_called_once_with("test_config")

    def test_get_company_list_function(self):
        """Test get_company_list convenience function"""
        with patch("common.config_manager.config_manager") as mock_cm:
            mock_cm.get_company_list.return_value = [{"ticker": "AAPL"}]

            result = get_company_list("magnificent_7")
            assert result == [{"ticker": "AAPL"}]
            mock_cm.get_company_list.assert_called_once_with("magnificent_7")

    def test_get_llm_config_function(self):
        """Test get_llm_config convenience function"""
        with patch("common.config_manager.config_manager") as mock_cm:
            mock_cm.get_llm_config.return_value = {"model": "test"}

            result = get_llm_config("default")
            assert result == {"model": "test"}
            mock_cm.get_llm_config.assert_called_once_with("default")

    def test_get_data_source_config_function(self):
        """Test get_data_source_config convenience function"""
        with patch("common.config_manager.config_manager") as mock_cm:
            mock_cm.get_data_source_config.return_value = {"source": "test"}

            result = get_data_source_config("sec_edgar", "stage_00")
            assert result == {"source": "test"}
            mock_cm.get_data_source_config.assert_called_once_with("sec_edgar", "stage_00")


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory for testing"""
        temp_dir = tempfile.mkdtemp()
        config_dir = Path(temp_dir)

        yield config_dir

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_missing_config_directory(self):
        """Test behavior when config directory doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_dir = Path(temp_dir) / "nonexistent"

            # Should not raise exception
            cm = ConfigManager(config_root=nonexistent_dir)
            assert cm._cache is not None

            # Should return empty configs
            assert cm.get_config("any_config") == {}

    def test_corrupted_config_file(self, temp_config_dir):
        """Test behavior with corrupted YAML file"""
        # Create corrupted YAML file
        corrupted_file = temp_config_dir / "corrupted.yml"
        with open(corrupted_file, "w") as f:
            f.write("invalid: yaml: content: [unclosed")

        # Add schema for corrupted config
        cm = ConfigManager(config_root=temp_config_dir)
        cm._schemas["corrupted"] = ConfigSchema(name="corrupted", path="corrupted.yml")

        # Should handle gracefully
        config = cm.get_config("corrupted")
        assert config == {}

    def test_json_config_support(self, temp_config_dir):
        """Test JSON configuration file support"""
        json_config = {"test": "json_data", "number": 123}
        json_file = temp_config_dir / "test.json"

        import json

        with open(json_file, "w") as f:
            json.dump(json_config, f)

        cm = ConfigManager(config_root=temp_config_dir)

        # Should load JSON files correctly
        loaded_config = cm._load_config_file(json_file)
        assert loaded_config == json_config

    def test_update_nonexistent_config(self):
        """Test updating non-existent configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cm = ConfigManager(config_root=Path(temp_dir))

            result = cm.update_config("nonexistent", {"test": "data"})
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
