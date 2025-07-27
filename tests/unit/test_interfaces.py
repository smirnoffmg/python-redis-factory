"""
Unit tests for the interfaces module.

This module tests the core interfaces and configuration classes.
"""

import pytest

from python_redis_factory.interfaces import (
    RedisConnectionConfig,
    RedisConnectionMode,
)


class TestRedisConnectionMode:
    """Test the RedisConnectionMode enum."""

    def test_enum_values(self):
        """Test that enum values are correctly defined."""
        assert RedisConnectionMode.STANDALONE.value == "standalone"
        assert RedisConnectionMode.SENTINEL.value == "sentinel"
        assert RedisConnectionMode.CLUSTER.value == "cluster"


class TestRedisConnectionConfig:
    """Test the RedisConnectionConfig class."""

    def test_basic_config_creation(self):
        """Test creating a basic configuration."""
        config = RedisConnectionConfig(host="localhost")

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.password is None
        assert config.db == 0
        assert config.mode == RedisConnectionMode.STANDALONE

    def test_full_config_creation(self):
        """Test creating a configuration with all parameters."""
        config = RedisConnectionConfig(
            host="redis.example.com",
            port=6380,
            password="secret",
            db=1,
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379", "sentinel2:26379"],
            service_name="mymaster",
            max_connections=20,
            socket_timeout=10.0,
            socket_connect_timeout=3.0,
            ssl=True,
        )

        assert config.host == "redis.example.com"
        assert config.port == 6380
        assert config.password == "secret"
        assert config.db == 1
        assert config.mode == RedisConnectionMode.SENTINEL
        assert config.sentinel_hosts == ["sentinel1:26379", "sentinel2:26379"]
        assert config.service_name == "mymaster"
        assert config.max_connections == 20
        assert config.socket_timeout == 10.0
        assert config.socket_connect_timeout == 3.0
        assert config.ssl is True

    def test_invalid_port_too_low(self):
        """Test that port validation rejects values below 1."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            RedisConnectionConfig(host="localhost", port=0)

    def test_invalid_port_too_high(self):
        """Test that port validation rejects values above 65535."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            RedisConnectionConfig(host="localhost", port=65536)

    def test_invalid_db_negative(self):
        """Test that database validation rejects negative values."""
        with pytest.raises(ValueError, match="Database number must be non-negative"):
            RedisConnectionConfig(host="localhost", db=-1)

    def test_invalid_max_connections(self):
        """Test that max_connections validation rejects values below 1."""
        with pytest.raises(ValueError, match="Max connections must be at least 1"):
            RedisConnectionConfig(host="localhost", max_connections=0)

    def test_invalid_socket_timeout(self):
        """Test that socket_timeout validation rejects negative values."""
        with pytest.raises(ValueError, match="Socket timeout must be non-negative"):
            RedisConnectionConfig(host="localhost", socket_timeout=-1.0)

    def test_invalid_socket_connect_timeout(self):
        """Test that socket_connect_timeout validation rejects negative values."""
        with pytest.raises(
            ValueError, match="Socket connect timeout must be non-negative"
        ):
            RedisConnectionConfig(host="localhost", socket_connect_timeout=-1.0)
