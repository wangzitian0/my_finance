# common/config.py
import os

import yaml


def load_common_config():
    """
    Load the common configuration from common_config.yml in the common directory.
    """
    config_path = os.path.join(os.path.dirname(__file__), "common_config.yml")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Common configuration file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config
