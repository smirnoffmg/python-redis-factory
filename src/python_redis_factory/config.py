"""
Configuration management module.

This module provides utilities for creating, validating, and managing
Redis connection configurations.
"""

from dataclasses import replace
from typing import Any, Optional

from .interfaces import RedisConnectionConfig, RedisConnectionMode
from .uri_parser import parse_redis_uri


def get_default_config(
    mode: Optional[RedisConnectionMode] = None,
) -> RedisConnectionConfig:
    """
    Get a default configuration for the specified mode.

    Args:
        mode: Connection mode (defaults to STANDALONE)

    Returns:
        Default RedisConnectionConfig for the specified mode
    """
    if mode is None:
        mode = RedisConnectionMode.STANDALONE

    config = RedisConnectionConfig(
        host="localhost",
        port=6379,
        password=None,
        db=0,
        mode=mode,
        max_connections=10,
        socket_timeout=5.0,
        socket_connect_timeout=5.0,
        ssl=False,
        ssl_cert_reqs=None,
        ssl_ca_certs=None,
    )

    # Set mode-specific defaults
    if mode == RedisConnectionMode.SENTINEL:
        config.sentinel_hosts = None
        config.sentinel_password = None
        config.service_name = None
    elif mode == RedisConnectionMode.CLUSTER:
        config.cluster_nodes = None

    return config


def create_config_from_uri(uri: str, **overrides: Any) -> RedisConnectionConfig:
    """
    Create a configuration from a Redis URI with optional overrides.

    Args:
        uri: Redis connection URI
        **overrides: Configuration parameters to override

    Returns:
        RedisConnectionConfig object
    """
    # Parse the URI to get base configuration
    config = parse_redis_uri(uri)

    # Apply overrides
    if overrides:
        config = replace(config, **overrides)

    return config


def merge_configs(
    base: RedisConnectionConfig, override: RedisConnectionConfig
) -> RedisConnectionConfig:
    """
    Merge two configurations, with override taking precedence.

    Args:
        base: Base configuration
        override: Configuration to merge on top of base

    Returns:
        Merged RedisConnectionConfig
    """
    # Build override dict with only non-None values
    overrides = {k: v for k, v in override.__dict__.items() if v is not None}

    return replace(base, **overrides)
