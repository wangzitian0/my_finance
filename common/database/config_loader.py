#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Database Configuration Loader

Supports configuration inheritance and override patterns for better maintainability.
Replaces the multiple separate configuration files with a base + override approach.

Issue #266: Improved configuration inheritance system
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class DatabaseConfigLoader:
    """
    Improved database configuration loader with inheritance support.
    
    Features:
    - Base configuration with environment-specific overrides
    - Deep merging of configuration dictionaries
    - Fallback to defaults when config files are missing
    - Environment variable substitution
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or Path("common/config")
        self._logger = logging.getLogger(__name__)
        
    def load_config(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration with inheritance and override support.
        
        Args:
            environment: Target environment (auto-detected if None)
            
        Returns:
            Merged configuration dictionary
        """
        environment = environment or self._detect_environment()
        
        try:
            # Load base configuration
            base_config = self._load_base_config()
            
            # Load environment-specific overrides
            override_config = self._load_override_config(environment)
            
            # Merge configurations
            merged_config = self._deep_merge(base_config, override_config)
            
            # Substitute environment variables
            final_config = self._substitute_env_vars(merged_config)
            
            self._logger.info(f"Loaded database configuration for environment: {environment}")
            return final_config
            
        except Exception as e:
            self._logger.warning(f"Failed to load configuration: {e}")
            return self._get_fallback_config(environment)
    
    def _detect_environment(self) -> str:
        """
        Detect current environment based on environment variables.
        
        Returns:
            Environment string: 'ci', 'production', or 'development'
        """
        if os.getenv('CI'):
            return 'ci'
        elif os.getenv('PRODUCTION') or os.getenv('NEO4J_PRODUCTION'):
            return 'production'
        else:
            return 'development'
    
    def _load_base_config(self) -> Dict[str, Any]:
        """
        Load base configuration that applies to all environments.
        
        Returns:
            Base configuration dictionary
        """
        base_file = self.config_dir / "database_base.yml"
        
        if base_file.exists() and YAML_AVAILABLE:
            return self._load_yaml_file(base_file)
        else:
            self._logger.warning("Base configuration file not found, using defaults")
            return self._get_default_base_config()
    
    def _load_override_config(self, environment: str) -> Dict[str, Any]:
        """
        Load environment-specific configuration overrides.
        
        Args:
            environment: Target environment
            
        Returns:
            Environment-specific configuration overrides
        """
        override_file = self.config_dir / "database_overrides.yml"
        
        if override_file.exists() and YAML_AVAILABLE:
            overrides_data = self._load_yaml_file(override_file)
            return overrides_data.get("environments", {}).get(environment, {})
        else:
            self._logger.warning(f"Override configuration file not found for environment: {environment}")
            return {}
    
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load YAML configuration file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Parsed YAML content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            self._logger.error(f"Failed to load YAML file {file_path}: {e}")
            return {}
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two configuration dictionaries.
        
        Override values take precedence over base values.
        Nested dictionaries are merged recursively.
        
        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary
            
        Returns:
            Merged configuration dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if (key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Substitute environment variables in configuration values.
        
        Supports ${VAR_NAME} and ${VAR_NAME:-default} syntax.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration with environment variables substituted
        """
        import re
        
        def substitute_value(value):
            if isinstance(value, str):
                # Pattern: ${VAR_NAME} or ${VAR_NAME:-default}
                pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
                
                def replace_var(match):
                    var_name = match.group(1)
                    default_value = match.group(2) if match.group(2) is not None else ''
                    return os.getenv(var_name, default_value)
                
                return re.sub(pattern, replace_var, value)
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            else:
                return value
        
        return substitute_value(config)
    
    def _get_default_base_config(self) -> Dict[str, Any]:
        """
        Get default base configuration when config files are not available.
        
        Returns:
            Default base configuration dictionary
        """
        return {
            'neo4j': {
                'port': 7687,
                'database': 'neo4j',
                'connection': {
                    'timeout': 30,
                    'max_retry_attempts': 3,
                    'pool_max_size': 50
                },
                'test_settings': {
                    'table_name': 'TestNode',
                    'cleanup_on_exit': False,
                    'performance_baseline_ms': 100
                },
                'monitoring': {
                    'health_check_interval': 60,
                    'enable_metrics': True,
                    'enable_crud_tests': True
                }
            }
        }
    
    def _get_fallback_config(self, environment: str) -> Dict[str, Any]:
        """
        Get fallback configuration when config loading fails.
        
        Args:
            environment: Target environment
            
        Returns:
            Fallback configuration dictionary
        """
        base_config = self._get_default_base_config()
        
        # Apply environment-specific defaults
        if environment == 'ci':
            base_config['neo4j']['host'] = 'localhost'
            base_config['neo4j']['auth'] = {'user': 'neo4j', 'password': 'ci_test_password'}
            base_config['neo4j']['connection']['timeout'] = 15
            base_config['neo4j']['connection']['pool_max_size'] = 10
            base_config['neo4j']['test_settings']['cleanup_on_exit'] = True
            base_config['neo4j']['test_settings']['performance_baseline_ms'] = 200
        elif environment == 'production':
            base_config['neo4j']['host'] = os.getenv('NEO4J_HOST', 'neo4j-prod.internal')
            base_config['neo4j']['port'] = int(os.getenv('NEO4J_PORT', '7687'))
            base_config['neo4j']['database'] = os.getenv('NEO4J_DATABASE', 'finance_prod')
            base_config['neo4j']['auth'] = {
                'user': os.getenv('NEO4J_USER', 'neo4j'),
                'password': os.getenv('NEO4J_PASSWORD', '')
            }
            base_config['neo4j']['connection']['timeout'] = 60
            base_config['neo4j']['connection']['pool_max_size'] = 100
            base_config['neo4j']['test_settings']['performance_baseline_ms'] = 50
            base_config['neo4j']['monitoring']['enable_crud_tests'] = False
        else:  # development
            base_config['neo4j']['host'] = 'localhost'
            base_config['neo4j']['auth'] = {'user': 'neo4j', 'password': 'finance123'}
        
        return base_config
    
    def get_available_environments(self) -> list:
        """
        Get list of available environment configurations.
        
        Returns:
            List of available environment names
        """
        override_file = self.config_dir / "database_overrides.yml"
        
        if override_file.exists() and YAML_AVAILABLE:
            overrides_data = self._load_yaml_file(override_file)
            return list(overrides_data.get("environments", {}).keys())
        else:
            return ['development', 'ci', 'production']
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate loaded configuration and return validation results.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        neo4j_config = config.get('neo4j', {})
        
        # Required fields
        required_fields = ['host', 'port', 'database', 'auth']
        for field in required_fields:
            if field not in neo4j_config:
                results['errors'].append(f"Missing required field: neo4j.{field}")
                results['valid'] = False
        
        # Auth validation
        auth_config = neo4j_config.get('auth', {})
        if not auth_config.get('password'):
            results['warnings'].append("Empty password detected")
        
        # Connection validation
        connection_config = neo4j_config.get('connection', {})
        timeout = connection_config.get('timeout', 30)
        if timeout < 5:
            results['warnings'].append(f"Very short timeout: {timeout}s")
        elif timeout > 300:
            results['warnings'].append(f"Very long timeout: {timeout}s")
        
        return results


# Global instance for easy access
config_loader = DatabaseConfigLoader()


def get_database_config(environment: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to get database configuration.
    
    Args:
        environment: Target environment (auto-detected if None)
        
    Returns:
        Database configuration dictionary
    """
    return config_loader.load_config(environment)