"""
Python Redis Factory - A universal Redis client factory.

This package provides a unified interface for connecting to Redis instances
regardless of deployment mode (standalone, Sentinel, or Cluster).
"""

from .config import (
    create_config_from_uri,
    get_default_config,
    merge_configs,
    validate_config,
)
from .interfaces import RedisConnectionConfig, RedisConnectionMode
from .simple_api import get_redis_client
from .uri_parser import parse_redis_uri

__version__ = "0.2.0"
__all__ = [
    "RedisConnectionConfig",
    "RedisConnectionMode",
    "get_redis_client",
    "parse_redis_uri",
    "create_config_from_uri",
    "get_default_config",
    "merge_configs",
    "validate_config",
]
