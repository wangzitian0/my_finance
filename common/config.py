# common/config.py
"""
DEPRECATED: This module is deprecated in favor of unified config_manager.py

Issue #185: Configuration SSOT Unification
- This file is replaced by config_manager.py which provides comprehensive configuration management
- All functions in this module now redirect to config_manager with deprecation warnings
- Legacy imports will continue to work but will show deprecation warnings

Migration Guide:
OLD: from common.config import load_common_config
NEW: from common.config_manager import config_manager; config_manager.get_config('common_config')
"""

import os
import warnings

import yaml


def load_common_config():
    """
    DEPRECATED: Load the common configuration from common_config.yml in the common directory.

    This function is deprecated. Use config_manager.get_config('common_config') instead.

    Migration:
        OLD: from common.config import load_common_config; config = load_common_config()
        NEW: from common.config_manager import config_manager; config = config_manager.get_config('common_config')
    """
    warnings.warn(
        "load_common_config() from common.config is deprecated. "
        "Use 'from common.config_manager import config_manager; config_manager.get_config('common_config')' instead. "
        "This function will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Redirect to config_manager for actual functionality
    try:
        from .config_manager import config_manager

        return config_manager.get_config("common_config")
    except ImportError:
        # Fallback to legacy implementation if config_manager not available
        config_path = os.path.join(os.path.dirname(__file__), "common_config.yml")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Common configuration file not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
