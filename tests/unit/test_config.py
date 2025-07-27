"""
Unit tests for configuration management.

This module tests configuration object creation, validation, merging, and default values.
"""

import pytest

from python_redis_factory.config import (
    create_config_from_uri,
    get_default_config,
    merge_configs,
    validate_config,
)
from python_redis_factory.interfaces import RedisConnectionConfig, RedisConnectionMode


class TestConfigurationManagement:
    """Test configuration management functionality."""

    def test_create_config_from_uri(self):
        """Test creating configuration from URI."""
        uri = "redis://localhost:6379"
        config = create_config_from_uri(uri)

        assert isinstance(config, RedisConnectionConfig)
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.mode == RedisConnectionMode.STANDALONE

    def test_create_config_from_uri_with_overrides(self):
        """Test creating configuration from URI with parameter overrides."""
        uri = "redis://localhost:6379"
        overrides = {"max_connections": 20, "socket_timeout": 10.0}
        config = create_config_from_uri(uri, **overrides)

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.max_connections == 20
        assert config.socket_timeout == 10.0

    def test_get_default_config(self):
        """Test getting default configuration."""
        config = get_default_config()

        assert isinstance(config, RedisConnectionConfig)
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
        assert config.mode == RedisConnectionMode.STANDALONE
        assert config.max_connections == 10
        assert config.socket_timeout == 5.0
        assert config.socket_connect_timeout == 5.0
        assert config.ssl is False

    def test_get_default_config_with_mode(self):
        """Test getting default configuration for specific mode."""
        config = get_default_config(mode=RedisConnectionMode.SENTINEL)

        assert config.mode == RedisConnectionMode.SENTINEL
        assert config.sentinel_hosts is None
        assert config.service_name is None

    def test_merge_configs_basic(self):
        """Test merging two configurations."""
        base_config = RedisConnectionConfig(
            host="localhost", port=6379, max_connections=10
        )
        override_config = RedisConnectionConfig(
            host="redis.example.com", port=6380, password="secret"
        )

        merged = merge_configs(base_config, override_config)

        assert merged.host == "redis.example.com"
        assert merged.port == 6380
        assert merged.password == "secret"
        assert merged.max_connections == 10  # Not overridden

    def test_merge_configs_with_none_values(self):
        """Test that None values in override don't overwrite base values."""
        base_config = RedisConnectionConfig(
            host="localhost", port=6379, password="base_password"
        )
        override_config = RedisConnectionConfig(
            host="redis.example.com",
            port=6380,
            password=None,  # Should not overwrite base password
        )

        merged = merge_configs(base_config, override_config)

        assert merged.host == "redis.example.com"
        assert merged.port == 6380
        assert merged.password == "base_password"  # Preserved from base

    def test_merge_configs_sentinel_specific(self):
        """Test merging Sentinel-specific configuration."""
        base_config = RedisConnectionConfig(
            host="localhost", mode=RedisConnectionMode.SENTINEL
        )
        override_config = RedisConnectionConfig(
            host="localhost",  # Required field
            mode=RedisConnectionMode.SENTINEL,  # Explicitly set mode
            sentinel_hosts=["sentinel1:26379", "sentinel2:26379"],
            service_name="mymaster",
        )

        merged = merge_configs(base_config, override_config)

        assert merged.mode == RedisConnectionMode.SENTINEL
        assert merged.sentinel_hosts == ["sentinel1:26379", "sentinel2:26379"]
        assert merged.service_name == "mymaster"

    def test_merge_configs_cluster_specific(self):
        """Test merging Cluster-specific configuration."""
        base_config = RedisConnectionConfig(
            host="localhost", mode=RedisConnectionMode.CLUSTER
        )
        override_config = RedisConnectionConfig(
            host="localhost",  # Required field
            mode=RedisConnectionMode.CLUSTER,  # Explicitly set mode
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        merged = merge_configs(base_config, override_config)

        assert merged.mode == RedisConnectionMode.CLUSTER
        assert merged.cluster_nodes == ["node1:7000", "node2:7001"]

    def test_validate_config_valid(self):
        """Test validating a valid configuration."""
        config = RedisConnectionConfig(
            host="localhost", port=6379, mode=RedisConnectionMode.STANDALONE
        )

        # Should not raise any exception
        validate_config(config)

    def test_validate_config_invalid_host(self):
        """Test validating configuration with invalid host."""
        config = RedisConnectionConfig(host="", port=6379)  # Empty host

        with pytest.raises(ValueError, match="Host cannot be empty"):
            validate_config(config)

    def test_validate_config_sentinel_missing_service_name(self):
        """Test validating Sentinel config without service name."""
        config = RedisConnectionConfig(
            host="localhost",
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379"],
            # Missing service_name
        )

        with pytest.raises(
            ValueError, match="Service name is required for Sentinel mode"
        ):
            validate_config(config)

    def test_validate_config_sentinel_missing_hosts(self):
        """Test validating Sentinel config without sentinel hosts."""
        config = RedisConnectionConfig(
            host="localhost",
            mode=RedisConnectionMode.SENTINEL,
            service_name="mymaster",
            # Missing sentinel_hosts
        )

        with pytest.raises(
            ValueError, match="Sentinel hosts are required for Sentinel mode"
        ):
            validate_config(config)

    def test_validate_config_cluster_missing_nodes(self):
        """Test validating Cluster config without cluster nodes."""
        config = RedisConnectionConfig(
            host="localhost",
            mode=RedisConnectionMode.CLUSTER,
            # Missing cluster_nodes
        )

        with pytest.raises(
            ValueError, match="Cluster nodes are required for Cluster mode"
        ):
            validate_config(config)

    def test_validate_config_ssl_without_cert_reqs(self):
        """Test validating SSL config without proper SSL settings."""
        config = RedisConnectionConfig(
            host="localhost",
            ssl=True,
            ssl_cert_reqs=None,  # Should be set for SSL
        )

        with pytest.raises(
            ValueError,
            match="SSL certificate requirements must be specified when SSL is enabled",
        ):
            validate_config(config)

    def test_create_config_from_dict(self):
        """Test creating configuration from dictionary."""
        config_dict = {
            "host": "redis.example.com",
            "port": 6380,
            "password": "secret",
            "db": 1,
            "max_connections": 20,
        }

        config = create_config_from_uri("redis://localhost:6379", **config_dict)

        assert config.host == "redis.example.com"
        assert config.port == 6380
        assert config.password == "secret"
        assert config.db == 1
        assert config.max_connections == 20
