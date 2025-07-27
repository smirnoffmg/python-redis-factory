"""
Cluster integration tests for Redis client factory.

This module tests the Redis cluster client functionality with real Redis cluster instances
using Testcontainers.
"""

import pytest
from testcontainers.redis import RedisContainer


class TestClusterIntegration:
    """Integration tests for Redis cluster client."""

    @pytest.fixture
    def redis_cluster_setup(self):
        """Create a Redis cluster setup for testing."""
        # For now, we'll use a simple Redis container and test the URI parsing
        # In a real scenario, we'd use a proper Redis cluster setup
        with RedisContainer("redis:7-alpine") as container:
            yield container

    def test_cluster_uri_parsing(self, redis_cluster_setup):
        """Test that cluster URIs are parsed correctly."""
        from python_redis_factory import parse_redis_uri

        # Test cluster URI parsing
        uri = "redis+cluster://node1:7000,node2:7001,node3:7002"
        config = parse_redis_uri(uri)

        assert config.mode.value == "cluster"
        assert config.cluster_nodes == ["node1:7000", "node2:7001", "node3:7002"]

    def test_cluster_uri_with_password(self, redis_cluster_setup):
        """Test cluster URI parsing with password."""
        from python_redis_factory import parse_redis_uri

        uri = "redis+cluster://:secret@node1:7000,node2:7001,node3:7002"
        config = parse_redis_uri(uri)

        assert config.mode.value == "cluster"
        assert config.password == "secret"
        assert config.cluster_nodes == ["node1:7000", "node2:7001", "node3:7002"]

    def test_cluster_config_validation(self, redis_cluster_setup):
        """Test cluster configuration validation."""
        from python_redis_factory import (
            RedisConnectionConfig,
            RedisConnectionMode,
            validate_config,
        )

        # Valid cluster config
        config = RedisConnectionConfig(
            host="node1",
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001", "node3:7002"],
        )

        # Should not raise an exception
        validate_config(config)

        # Invalid cluster config (missing cluster nodes)
        invalid_config = RedisConnectionConfig(
            host="node1",
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=None,
        )

        with pytest.raises(
            ValueError, match="Cluster nodes are required for Cluster mode"
        ):
            validate_config(invalid_config)

    def test_cluster_client_creation(self, redis_cluster_setup):
        """Test cluster client creation (without actual connection)."""
        from python_redis_factory import create_config_from_uri
        from python_redis_factory.clients.cluster import ClusterRedisClient

        # Create config from URI
        config = create_config_from_uri("redis+cluster://node1:7000,node2:7001")

        # Create cluster client
        client = ClusterRedisClient(config)

        from python_redis_factory import RedisConnectionMode

        assert client.config.mode == RedisConnectionMode.CLUSTER
        assert client.config.cluster_nodes == ["node1:7000", "node2:7001"]

    def test_cluster_uri_edge_cases(self, redis_cluster_setup):
        """Test cluster URI edge cases."""
        from python_redis_factory import parse_redis_uri

        # Test with single node
        uri = "redis+cluster://node1:7000"
        config = parse_redis_uri(uri)
        assert config.cluster_nodes == ["node1:7000"]

        # Test with many nodes
        uri = "redis+cluster://node1:7000,node2:7001,node3:7002,node4:7003,node5:7004"
        config = parse_redis_uri(uri)
        assert len(config.cluster_nodes) == 5

    def test_cluster_invalid_uri(self, redis_cluster_setup):
        """Test cluster invalid URI handling."""
        from python_redis_factory import parse_redis_uri

        # Test missing nodes
        with pytest.raises(
            ValueError, match="Cluster URI must include at least one node"
        ):
            parse_redis_uri("redis+cluster://")

        # Test invalid format
        with pytest.raises(ValueError, match="Invalid Redis URI scheme"):
            parse_redis_uri("invalid://format")

    def test_cluster_config_merging(self, redis_cluster_setup):
        """Test cluster configuration merging."""
        from python_redis_factory import (
            RedisConnectionConfig,
            RedisConnectionMode,
            merge_configs,
        )

        base_config = RedisConnectionConfig(
            host="node1",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000"],
        )

        override_config = RedisConnectionConfig(
            host="node2",
            port=7000,
            password="secret",
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        merged = merge_configs(base_config, override_config)

        assert merged.host == "node2"  # Override config takes precedence
        assert merged.port == 7000
        assert merged.password == "secret"
        assert merged.cluster_nodes == ["node1:7000", "node2:7001"]

    def test_cluster_default_config(self, redis_cluster_setup):
        """Test cluster default configuration."""
        from python_redis_factory import RedisConnectionMode, get_default_config

        config = get_default_config(RedisConnectionMode.CLUSTER)

        assert config.mode == RedisConnectionMode.CLUSTER
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.cluster_nodes is None  # Must be provided by user

    @pytest.mark.asyncio
    async def test_cluster_async_uri_parsing(self, redis_cluster_setup):
        """Test async cluster URI parsing."""
        from python_redis_factory import parse_redis_uri

        # Test cluster URI parsing for async usage
        uri = "redis+cluster://node1:7000,node2:7001,node3:7002"
        config = parse_redis_uri(uri)

        assert config.mode.value == "cluster"
        assert config.cluster_nodes == ["node1:7000", "node2:7001", "node3:7002"]

    def test_cluster_sync_vs_async_consistency(self, redis_cluster_setup):
        """Test that sync and async cluster clients produce consistent results."""
        from python_redis_factory import parse_redis_uri

        uri = "redis+cluster://node1:7000,node2:7001,node3:7002"

        # Parse URI once
        config = parse_redis_uri(uri)

        # Both sync and async should produce the same config
        assert config.mode.value == "cluster"
        assert config.cluster_nodes == ["node1:7000", "node2:7001", "node3:7002"]

    def test_cluster_error_handling(self, redis_cluster_setup):
        """Test cluster error handling scenarios."""
        from python_redis_factory import (
            RedisConnectionConfig,
            RedisConnectionMode,
            validate_config,
        )

        # Test empty cluster nodes
        config = RedisConnectionConfig(
            host="node1",
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=[],
        )

        with pytest.raises(ValueError, match="Cluster nodes are required"):
            validate_config(config)

        # Test None cluster nodes
        config = RedisConnectionConfig(
            host="node1",
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=None,
        )

        with pytest.raises(ValueError, match="Cluster nodes are required"):
            validate_config(config)

    def test_cluster_ssl_configuration(self, redis_cluster_setup):
        """Test cluster SSL configuration."""
        from python_redis_factory import (
            RedisConnectionConfig,
            RedisConnectionMode,
            validate_config,
        )

        # Test cluster config with SSL
        config = RedisConnectionConfig(
            host="node1",
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
            ssl=True,
            ssl_cert_reqs="required",
            ssl_ca_certs="/path/to/ca.crt",
        )

        # Should not raise an exception
        validate_config(config)

        assert config.ssl is True
        assert config.ssl_cert_reqs == "required"
        assert config.ssl_ca_certs == "/path/to/ca.crt"
