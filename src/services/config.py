"""
Configuration Management for HAR Parser Services

Handles loading configuration from environment variables, config files,
or defaults for flexible service deployment.
"""

import os
import json
from pathlib import Path

from services import ParserConfig


def load_config_from_env() -> ParserConfig:
    """Load parser configuration from environment variables."""
    service_type = os.getenv("HAR_PARSER_SERVICE", "local")

    # Service-specific configuration
    if service_type == "api":
        return ParserConfig(
            service_type="api",
            base_url=os.getenv("HAR_PARSER_API_URL", "http://localhost:8080"),
            api_key=os.getenv("HAR_PARSER_API_KEY"),
            timeout=int(os.getenv("HAR_PARSER_API_TIMEOUT", "30")),
        )
    elif service_type == "local":
        return ParserConfig(
            service_type="local", parser_module_path=os.getenv("HAR_PARSER_MODULE_PATH")
        )
    else:
        # Default to local
        return ParserConfig(service_type="local")


def load_config_from_file(config_path: str) -> ParserConfig:
    """Load parser configuration from JSON file."""
    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)

        service_type = config_data.get("service_type", "local")
        service_kwargs = config_data.get("service_config", {})

        return ParserConfig(service_type=service_type, **service_kwargs)

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Could not load config from {config_path}: {e}")
        return ParserConfig(service_type="local")


def get_config() -> ParserConfig:
    """
    Get parser configuration from environment or default.

    Priority:
    1. CONFIG_FILE environment variable pointing to JSON config
    2. Environment variables
    3. Default local configuration
    """
    config_file = os.getenv("HAR_PARSER_CONFIG_FILE")

    if config_file and Path(config_file).exists():
        return load_config_from_file(config_file)
    else:
        return load_config_from_env()


# Sample configuration files for reference:

SAMPLE_LOCAL_CONFIG = {
    "service_type": "local",
    "service_config": {"parser_module_path": None},
}

SAMPLE_API_CONFIG = {
    "service_type": "api",
    "service_config": {
        "base_url": "https://your-parser-api.com",
        "api_key": "your-api-key-here",
        "timeout": 30,
    },
}
