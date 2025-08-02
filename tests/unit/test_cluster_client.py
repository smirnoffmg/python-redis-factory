"""
Unit tests for the Cluster Redis client.

This module tests the Cluster Redis client creation and basic operations.
"""

from unittest.mock import Mock, patch

import pytest
from redis.cluster import ClusterNode

from python_redis_factory.clients.cluster import ClusterRedisClient
from python_redis_factory.interfaces import RedisConnectionConfig, RedisConnectionMode


class TestClusterRedisClient:
    """Test the Cluster Redis client functionality."""

    @pytest.mark.asyncio
    async def test_create_cluster_connection(self):
        """Test that Cluster connection is created with correct parameters."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            password="secret",
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
            ssl=True,
            ssl_cert_reqs="required",
        )

        with patch(
            "python_redis_factory.clients.cluster.RedisCluster"
        ) as mock_redis_cluster:
            mock_instance = Mock()
            mock_redis_cluster.return_value = mock_instance

            await ClusterRedisClient.create(config)

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

    @pytest.mark.asyncio
    async def test_create_cluster_connection_with_ssl(self):
        """Test that Cluster connection is created with SSL parameters."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
            ssl=True,
            ssl_cert_reqs="required",
        )

        with patch(
            "python_redis_factory.clients.cluster.RedisCluster"
        ) as mock_redis_cluster:
            mock_instance = Mock()
            mock_redis_cluster.return_value = mock_instance

            await ClusterRedisClient.create(config)

            # Verify SSL parameters were passed
            call_args = mock_redis_cluster.call_args[1]
            assert call_args["ssl"] is True
            assert call_args["ssl_cert_reqs"] == "required"

    @pytest.mark.asyncio
    async def test_create_cluster_connection_defaults(self):
        """Test that Cluster connection uses default values when not specified."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with patch(
            "python_redis_factory.clients.cluster.RedisCluster"
        ) as mock_redis_cluster:
            mock_instance = Mock()
            mock_redis_cluster.return_value = mock_instance

            await ClusterRedisClient.create(config)

            # Verify default values were used
            call_args = mock_redis_cluster.call_args[1]
            assert "ssl" not in call_args
            assert call_args["decode_responses"] is True
            assert "startup_nodes" in call_args

    @pytest.mark.asyncio
    async def test_validate_config_wrong_mode(self):
        """Test that client rejects configuration with wrong mode."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.STANDALONE,  # Wrong mode
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with pytest.raises(ValueError, match="Configuration must be for CLUSTER mode"):
            await ClusterRedisClient.create(config)

    @pytest.mark.asyncio
    async def test_validate_config_missing_cluster_nodes(self):
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
            await ClusterRedisClient.create(config)

    @pytest.mark.asyncio
    async def test_basic_redis_operations(self):
        """Test basic Redis operations work correctly."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with patch(
            "python_redis_factory.clients.cluster.RedisCluster"
        ) as mock_redis_cluster:
            mock_instance = Mock()
            mock_instance.ping.return_value = True
            mock_instance.set.return_value = True
            mock_instance.get.return_value = "test_value"
            mock_redis_cluster.return_value = mock_instance

            redis_client = await ClusterRedisClient.create(config)

            # Test basic operations
            assert redis_client.ping() is True
            assert redis_client.set("test_key", "test_value") is True
            assert redis_client.get("test_key") == "test_value"

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test that connection errors are handled properly."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with patch(
            "python_redis_factory.clients.cluster.RedisCluster"
        ) as mock_redis_cluster:
            mock_redis_cluster.side_effect = Exception("Connection failed")

            with pytest.raises(Exception, match="Connection failed"):
                await ClusterRedisClient.create(config)

    @pytest.mark.asyncio
    async def test_create_async_cluster_connection(self):
        """Test that async Cluster connection is created with correct parameters."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            password="secret",
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with patch(
            "python_redis_factory.clients.cluster.AsyncRedisCluster"
        ) as mock_redis_cluster:
            mock_instance = Mock()
            mock_redis_cluster.return_value = mock_instance

            await ClusterRedisClient.create(config, async_client=True)

            # Verify async RedisCluster was called with correct parameters
            mock_redis_cluster.assert_called_once()
            call_args = mock_redis_cluster.call_args[1]

            assert "startup_nodes" in call_args
            assert len(call_args["startup_nodes"]) == 2
            assert call_args["startup_nodes"][0].host == "node1"
            assert call_args["startup_nodes"][0].port == 7000
            assert call_args["startup_nodes"][1].host == "node2"
            assert call_args["startup_nodes"][1].port == 7001
            assert call_args["password"] == "secret"
            assert call_args["decode_responses"] is True
