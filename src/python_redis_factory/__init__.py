"""Python Redis Factory."""

__version__ = "0.1.0"

from .clients import ClusterRedisClient, SentinelRedisClient, StandaloneRedisClient
from .config import (
    create_config_from_uri,
    get_default_config,
    merge_configs,
)
from .interfaces import RedisConnectionConfig, RedisConnectionMode
from .simple_api import get_redis_client
from .uri_parser import parse_redis_uri

__all__ = [
    "create_config_from_uri",
    "get_default_config",
    "get_redis_client",
    "merge_configs",
    "parse_redis_uri",
    "RedisConnectionConfig",
    "RedisConnectionMode",
    "StandaloneRedisClient",
    "SentinelRedisClient",
    "ClusterRedisClient",
]
