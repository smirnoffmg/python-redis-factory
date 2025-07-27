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
        override_config = RedisConnectionConfig(
            host=overrides.get("host", config.host),
            port=overrides.get("port", config.port),
            password=overrides.get("password", config.password),
            db=overrides.get("db", config.db),
            mode=overrides.get("mode", config.mode),
            sentinel_hosts=overrides.get("sentinel_hosts", config.sentinel_hosts),
            sentinel_password=overrides.get(
                "sentinel_password", config.sentinel_password
            ),
            service_name=overrides.get("service_name", config.service_name),
            cluster_nodes=overrides.get("cluster_nodes", config.cluster_nodes),
            max_connections=overrides.get("max_connections", config.max_connections),
            socket_timeout=overrides.get("socket_timeout", config.socket_timeout),
            socket_connect_timeout=overrides.get(
                "socket_connect_timeout", config.socket_connect_timeout
            ),
            ssl=overrides.get("ssl", config.ssl),
            ssl_cert_reqs=overrides.get("ssl_cert_reqs", config.ssl_cert_reqs),
            ssl_ca_certs=overrides.get("ssl_ca_certs", config.ssl_ca_certs),
        )
        config = override_config

    # Validate the final configuration
    validate_config(config)

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


def validate_config(config: RedisConnectionConfig) -> None:
    """
    Validate a Redis connection configuration.

    Args:
        config: Configuration to validate

    Raises:
        ValueError: If configuration is invalid
    """
    # Basic validation (already done in __post_init__, but we add mode-specific validation)
    if not config.host or config.host.strip() == "":
        raise ValueError("Host cannot be empty")

    # Mode-specific validation
    if config.mode == RedisConnectionMode.SENTINEL:
        if not config.service_name:
            raise ValueError("Service name is required for Sentinel mode")
        if not config.sentinel_hosts:
            raise ValueError("Sentinel hosts are required for Sentinel mode")

    elif config.mode == RedisConnectionMode.CLUSTER:
        if not config.cluster_nodes:
            raise ValueError("Cluster nodes are required for Cluster mode")

    # SSL validation
    if config.ssl and config.ssl_cert_reqs is None:
        raise ValueError(
            "SSL certificate requirements must be specified when SSL is enabled"
        )
