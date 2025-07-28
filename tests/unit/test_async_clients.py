"""
Unit tests for async Redis clients.

This module tests the async Redis client wrappers for different deployment modes.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from python_redis_factory.clients import (
    ClusterRedisClient,
    SentinelRedisClient,
    StandaloneRedisClient,
)
from python_redis_factory.interfaces import RedisConnectionConfig, RedisConnectionMode


class TestAsyncStandaloneRedisClient:
    """Test the async standalone Redis client functionality."""

    def test_create_async_standalone_client(self):
        """Test creating an async standalone Redis client."""
        config = RedisConnectionConfig(
            host="localhost",
            port=6379,
            mode=RedisConnectionMode.STANDALONE,
        )
        client = StandaloneRedisClient(config, async_client=True)
        assert client.config == config
        assert client.config.mode == RedisConnectionMode.STANDALONE
        assert client.async_client is True

    def test_create_async_standalone_connection(self):
        """Test that async standalone connection is created with correct parameters."""
        config = RedisConnectionConfig(
            host="localhost",
            port=6379,
            password="secret",
            mode=RedisConnectionMode.STANDALONE,
            ssl=True,
            ssl_cert_reqs="required",
        )

        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_redis.return_value = mock_instance

            client = StandaloneRedisClient(config, async_client=True)
            client.create_connection()

            # Verify Redis was called with correct parameters
            mock_redis.assert_called_once()
            call_args = mock_redis.call_args[1]

            assert call_args["host"] == "localhost"
            assert call_args["port"] == 6379
            assert call_args["password"] == "secret"
            assert call_args["ssl"] is True
            assert call_args["ssl_cert_reqs"] == "required"
            assert call_args["decode_responses"] is True

    def test_validate_config_wrong_mode(self):
        """Test that client rejects configuration with wrong mode."""
        config = RedisConnectionConfig(
            host="localhost",
            port=6379,
            mode=RedisConnectionMode.SENTINEL,  # Wrong mode
        )

        with pytest.raises(
            ValueError, match="Configuration must be for STANDALONE mode"
        ):
            StandaloneRedisClient(config, async_client=True)

    @pytest.mark.asyncio
    async def test_async_redis_operations(self):
        """Test async Redis operations work correctly."""
        config = RedisConnectionConfig(
            host="localhost",
            port=6379,
            mode=RedisConnectionMode.STANDALONE,
        )

        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_instance.ping.return_value = True
            mock_instance.set.return_value = True
            mock_instance.get.return_value = "test_value"
            mock_redis.return_value = mock_instance

            client = StandaloneRedisClient(config, async_client=True)
            redis_client = client.create_connection()

            # Test async operations
            assert await redis_client.ping() is True
            assert await redis_client.set("test_key", "test_value") is True
            assert await redis_client.get("test_key") == "test_value"

    def test_client_repr(self):
        """Test that client has a meaningful string representation."""
        config = RedisConnectionConfig(
            host="localhost",
            port=6379,
            mode=RedisConnectionMode.STANDALONE,
        )
        client = StandaloneRedisClient(config, async_client=True)
        repr_str = repr(client)
        assert "AsyncStandaloneRedisClient" in repr_str
        assert "localhost:6379" in repr_str
        assert "STANDALONE" in repr_str


class TestAsyncSentinelRedisClient:
    """Test the async Sentinel Redis client functionality."""

    def test_create_async_sentinel_client(self):
        """Test creating an async Sentinel Redis client."""
        config = RedisConnectionConfig(
            host="localhost",
            port=26379,
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379"],
            service_name="mymaster",
        )
        client = SentinelRedisClient(config, async_client=True)
        assert client.config == config
        assert client.config.mode == RedisConnectionMode.SENTINEL
        assert client.async_client is True

    def test_create_async_sentinel_connection(self):
        """Test that async Sentinel connection is created with correct parameters."""
        config = RedisConnectionConfig(
            host="localhost",
            port=26379,
            password="secret",
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379"],
            service_name="mymaster",
            ssl=True,
            ssl_cert_reqs="required",
        )

        with patch("redis.asyncio.sentinel.Sentinel") as mock_sentinel:
            mock_sentinel_instance = AsyncMock()
            mock_sentinel.return_value = mock_sentinel_instance
            mock_master_client = AsyncMock()
            mock_sentinel_instance.master_for.return_value = mock_master_client

            client = SentinelRedisClient(config, async_client=True)
            client.create_connection()

            # Verify Sentinel was called with correct parameters
            mock_sentinel.assert_called_once()
            call_args = mock_sentinel.call_args[1]

            assert call_args["password"] == "secret"
            assert call_args["ssl"] is True
            assert call_args["ssl_cert_reqs"] == "required"
            assert call_args["decode_responses"] is True

    def test_validate_config_wrong_mode(self):
        """Test that client rejects configuration with wrong mode."""
        config = RedisConnectionConfig(
            host="localhost",
            port=26379,
            mode=RedisConnectionMode.STANDALONE,  # Wrong mode
            sentinel_hosts=["sentinel1:26379"],
            service_name="mymaster",
        )

        with pytest.raises(ValueError, match="Configuration must be for SENTINEL mode"):
            SentinelRedisClient(config, async_client=True)

    def test_validate_config_missing_sentinel_hosts(self):
        """Test that client rejects configuration without sentinel hosts."""
        config = RedisConnectionConfig(
            host="localhost",
            port=26379,
            mode=RedisConnectionMode.SENTINEL,
            # Missing sentinel_hosts
            service_name="mymaster",
        )

        with pytest.raises(
            ValueError, match="Sentinel hosts are required for Sentinel mode"
        ):
            SentinelRedisClient(config, async_client=True)

    def test_validate_config_missing_service_name(self):
        """Test that client rejects configuration without service name."""
        config = RedisConnectionConfig(
            host="localhost",
            port=26379,
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379"],
            # Missing service_name
        )

        with pytest.raises(
            ValueError, match="Service name is required for Sentinel mode"
        ):
            SentinelRedisClient(config, async_client=True)

    @pytest.mark.asyncio
    async def test_async_sentinel_operations(self):
        """Test async Sentinel Redis operations work correctly."""
        config = RedisConnectionConfig(
            host="localhost",
            port=26379,
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379"],
            service_name="mymaster",
        )

        with patch("redis.asyncio.sentinel.Sentinel") as mock_sentinel:
            mock_sentinel_instance = AsyncMock()
            mock_sentinel.return_value = mock_sentinel_instance
            mock_master_client = AsyncMock()
            mock_master_client.ping.return_value = True
            mock_master_client.set.return_value = True
            mock_master_client.get.return_value = "test_value"
            # Fix: master_for should return the mock client directly, not a coroutine
            mock_sentinel_instance.master_for = Mock(return_value=mock_master_client)

            client = SentinelRedisClient(config, async_client=True)
            redis_client = client.create_connection()

            # Test async operations
            assert await redis_client.ping() is True
            assert await redis_client.set("test_key", "test_value") is True
            assert await redis_client.get("test_key") == "test_value"

    def test_client_repr(self):
        """Test that client has a meaningful string representation."""
        config = RedisConnectionConfig(
            host="localhost",
            port=26379,
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379"],
            service_name="mymaster",
        )
        client = SentinelRedisClient(config, async_client=True)
        repr_str = repr(client)
        assert "AsyncSentinelRedisClient" in repr_str
        assert "sentinel1:26379" in repr_str
        assert "mymaster" in repr_str


class TestAsyncClusterRedisClient:
    """Test the async Cluster Redis client functionality."""

    def test_create_async_cluster_client(self):
        """Test creating an async Cluster Redis client."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001", "node3:7002"],
        )
        client = ClusterRedisClient(config, async_client=True)
        assert client.config == config
        assert client.config.mode == RedisConnectionMode.CLUSTER
        assert client.async_client is True

    def test_create_async_cluster_connection(self):
        """Test that async Cluster connection is created with correct parameters."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            password="secret",
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
            ssl=True,
            ssl_cert_reqs="required",
        )

        with patch("redis.asyncio.RedisCluster") as mock_redis_cluster:
            mock_instance = AsyncMock()
            mock_redis_cluster.return_value = mock_instance

            client = ClusterRedisClient(config, async_client=True)
            client.create_connection()

            # Verify RedisCluster was called with correct parameters
            mock_redis_cluster.assert_called_once()
            call_args = mock_redis_cluster.call_args[1]

            assert "startup_nodes" in call_args
            assert len(call_args["startup_nodes"]) == 2
            assert call_args["startup_nodes"][0].host == "node1"
            assert call_args["startup_nodes"][0].port == 7000
            assert call_args["startup_nodes"][1].host == "node2"
            assert call_args["startup_nodes"][1].port == 7001
            assert call_args["password"] == "secret"
            assert call_args["ssl"] is True
            assert call_args["ssl_cert_reqs"] == "required"
            assert call_args["decode_responses"] is True

    def test_validate_config_wrong_mode(self):
        """Test that client rejects configuration with wrong mode."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.STANDALONE,  # Wrong mode
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with pytest.raises(ValueError, match="Configuration must be for CLUSTER mode"):
            ClusterRedisClient(config, async_client=True)

    def test_validate_config_missing_cluster_nodes(self):
        """Test that client rejects configuration without cluster nodes."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            # Missing cluster_nodes
        )

        with pytest.raises(
            ValueError, match="Cluster nodes are required for Cluster mode"
        ):
            ClusterRedisClient(config, async_client=True)

    @pytest.mark.asyncio
    async def test_async_cluster_operations(self):
        """Test async Cluster Redis operations work correctly."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with patch("redis.asyncio.RedisCluster") as mock_redis_cluster:
            mock_instance = AsyncMock()
            mock_instance.ping.return_value = True
            mock_instance.set.return_value = True
            mock_instance.get.return_value = "test_value"
            mock_redis_cluster.return_value = mock_instance

            client = ClusterRedisClient(config, async_client=True)
            redis_client = client.create_connection()

            # Test async operations
            assert await redis_client.ping() is True
            assert await redis_client.set("test_key", "test_value") is True
            assert await redis_client.get("test_key") == "test_value"

    def test_client_repr(self):
        """Test that client has a meaningful string representation."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
        )
        client = ClusterRedisClient(config, async_client=True)
        repr_str = repr(client)
        assert "AsyncClusterRedisClient" in repr_str
        assert "localhost:7000" in repr_str
        assert "CLUSTER" in repr_str
