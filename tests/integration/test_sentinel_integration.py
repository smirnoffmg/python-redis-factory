"""
Integration tests for Sentinel Redis client.

This module tests the Sentinel Redis client with real Redis Sentinel instances
using Testcontainers.
"""

import pytest
from testcontainers.redis import RedisContainer


class TestSentinelIntegration:
    """Integration tests for Sentinel Redis client."""

    @pytest.fixture
    def redis_sentinel_setup(self):
        """Create a Redis Sentinel setup for testing."""
        # For now, we'll use a simple Redis container and test the URI parsing
        # In a real scenario, we'd use a proper Sentinel setup
        with RedisContainer("redis:7-alpine") as container:
            yield container

    def test_sentinel_uri_parsing(self, redis_sentinel_setup):
        """Test that Sentinel URIs are parsed correctly."""
        from python_redis_factory import parse_redis_uri

        # Test Sentinel URI parsing
        uri = "redis+sentinel://sentinel1:26379,sentinel2:26379/mymaster"
        config = parse_redis_uri(uri)

        assert config.mode.value == "sentinel"
        assert config.sentinel_hosts == ["sentinel1:26379", "sentinel2:26379"]
        assert config.service_name == "mymaster"

    def test_sentinel_uri_with_password(self, redis_sentinel_setup):
        """Test Sentinel URI parsing with password."""
        from python_redis_factory import parse_redis_uri

        uri = "redis+sentinel://:secret@sentinel1:26379,sentinel2:26379/mymaster"
        config = parse_redis_uri(uri)

        assert config.mode.value == "sentinel"
        assert config.password == "secret"
        assert config.sentinel_hosts == ["sentinel1:26379", "sentinel2:26379"]
        assert config.service_name == "mymaster"

    def test_sentinel_config_validation(self, redis_sentinel_setup):
        """Test Sentinel configuration validation."""
        from python_redis_factory import (
            RedisConnectionConfig,
            RedisConnectionMode,
            validate_config,
        )

        # Valid Sentinel config
        config = RedisConnectionConfig(
            host="sentinel1",
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379", "sentinel2:26379"],
            service_name="mymaster",
        )

        # Should not raise an exception
        validate_config(config)

        # Invalid Sentinel config (missing service name)
        invalid_config = RedisConnectionConfig(
            host="sentinel1",
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379"],
            service_name=None,
        )

        with pytest.raises(
            ValueError, match="Service name is required for Sentinel mode"
        ):
            validate_config(invalid_config)

    def test_sentinel_client_creation(self, redis_sentinel_setup):
        """Test Sentinel client creation (without actual connection)."""
        from python_redis_factory import create_config_from_uri
        from python_redis_factory.clients.sentinel import SentinelRedisClient

        # Create config from URI
        config = create_config_from_uri("redis+sentinel://sentinel1:26379/mymaster")

        # Create Sentinel client
        client = SentinelRedisClient(config)

        from python_redis_factory import RedisConnectionMode

        assert client.config.mode == RedisConnectionMode.SENTINEL
        assert client.config.sentinel_hosts == ["sentinel1:26379"]
        assert client.config.service_name == "mymaster"

    def test_sentinel_uri_edge_cases(self, redis_sentinel_setup):
        """Test Sentinel URI edge cases."""
        from python_redis_factory import parse_redis_uri

        # Test with single sentinel
        uri1 = "redis+sentinel://sentinel1:26379/mymaster"
        config1 = parse_redis_uri(uri1)
        assert config1.sentinel_hosts == ["sentinel1:26379"]

        # Test with multiple sentinels
        uri2 = (
            "redis+sentinel://sentinel1:26379,sentinel2:26380,sentinel3:26381/mymaster"
        )
        config2 = parse_redis_uri(uri2)
        assert config2.sentinel_hosts == [
            "sentinel1:26379",
            "sentinel2:26380",
            "sentinel3:26381",
        ]

    def test_sentinel_invalid_uri(self, redis_sentinel_setup):
        """Test Sentinel URI validation."""
        from python_redis_factory import parse_redis_uri

        # Missing service name
        with pytest.raises(ValueError, match="Sentinel URI must include service name"):
            parse_redis_uri("redis+sentinel://sentinel1:26379")

        # Invalid sentinel hosts
        with pytest.raises(
            ValueError, match="Sentinel URI must include at least one sentinel host"
        ):
            parse_redis_uri("redis+sentinel:///mymaster")

    def test_sentinel_config_merging(self, redis_sentinel_setup):
        """Test Sentinel configuration merging."""
        from python_redis_factory import create_config_from_uri, merge_configs

        # Base config
        base_config = create_config_from_uri(
            "redis+sentinel://sentinel1:26379/mymaster"
        )

        # Override config
        override_config = create_config_from_uri(
            "redis+sentinel://sentinel2:26380/mymaster"
        )

        # Merge configs
        merged_config = merge_configs(base_config, override_config)

        assert merged_config.sentinel_hosts == ["sentinel2:26380"]
        assert merged_config.service_name == "mymaster"

    def test_sentinel_default_config(self, redis_sentinel_setup):
        """Test Sentinel default configuration."""
        from python_redis_factory import RedisConnectionMode, get_default_config

        config = get_default_config(RedisConnectionMode.SENTINEL)

        assert config.mode == RedisConnectionMode.SENTINEL
        assert config.sentinel_hosts is None  # Will be set by user
        assert config.service_name is None  # Will be set by user
        assert config.max_connections == 10
        assert config.socket_timeout == 5.0
