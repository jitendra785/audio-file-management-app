import os
import yaml
from pathlib import Path
from typing import Dict, Any


class AppConfig:
    """Application configuration manager"""

    def __init__(self):
        self._config: Dict[str, Any] = {}

    def load(self) -> None:
        """Load configuration based on APP_ENV environment variable"""
        env = os.getenv('APP_ENV', 'LOCAL')
        config_path = Path(__file__).parent.parent.parent / 'environments' / f'{env}.yml'

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: get('database.postgres.host')
        """
        keys = key_path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default

        return value

    @property
    def all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config


# Global configuration instance
_config = AppConfig()


def load_config() -> None:
    """Load application configuration"""
    _config.load()


def get_config() -> AppConfig:
    """Get configuration instance"""
    return _config
