"""
Unit tests for the Cluster Redis client.

This module tests the Cluster Redis client creation and basic operations.
"""

from unittest.mock import Mock, patch

import pytest

from python_redis_factory.clients.cluster import ClusterRedisClient
from python_redis_factory.interfaces import RedisConnectionConfig, RedisConnectionMode


class TestClusterRedisClient:
    """Test the Cluster Redis client functionality."""

    def test_create_cluster_client(self):
        """Test creating a Cluster Redis client."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001", "node3:7002"],
        )
        client = ClusterRedisClient(config)
        assert client.config == config
        assert client.config.mode == RedisConnectionMode.CLUSTER

    def test_create_cluster_connection(self):
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

        with patch("redis.RedisCluster") as mock_redis_cluster:
            mock_instance = Mock()
            mock_redis_cluster.return_value = mock_instance

            client = ClusterRedisClient(config)
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

    def test_create_cluster_connection_with_ssl(self):
        """Test that Cluster connection is created with SSL parameters."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
            ssl=True,
            ssl_cert_reqs="required",
        )

        with patch("redis.RedisCluster") as mock_redis_cluster:
            mock_instance = Mock()
            mock_redis_cluster.return_value = mock_instance

            client = ClusterRedisClient(config)
            client.create_connection()

            # Verify SSL parameters were passed
            call_args = mock_redis_cluster.call_args[1]
            assert call_args["ssl"] is True
            assert call_args["ssl_cert_reqs"] == "required"

    def test_create_cluster_connection_defaults(self):
        """Test that Cluster connection uses default values when not specified."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with patch("redis.RedisCluster") as mock_redis_cluster:
            mock_instance = Mock()
            mock_redis_cluster.return_value = mock_instance

            client = ClusterRedisClient(config)
            client.create_connection()

            # Verify default values were used
            call_args = mock_redis_cluster.call_args[1]
            assert call_args["ssl"] is False
            assert call_args["decode_responses"] is True
            assert "startup_nodes" in call_args

    def test_validate_config_wrong_mode(self):
        """Test that client rejects configuration with wrong mode."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.STANDALONE,  # Wrong mode
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with pytest.raises(ValueError, match="Configuration must be for CLUSTER mode"):
            ClusterRedisClient(config)

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
            ClusterRedisClient(config)

    def test_validate_config_empty_cluster_nodes(self):
        """Test that client rejects configuration with empty cluster nodes."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=[],  # Empty list
        )

        with pytest.raises(
            ValueError, match="Cluster nodes are required for Cluster mode"
        ):
            ClusterRedisClient(config)

    def test_basic_redis_operations(self):
        """Test basic Redis operations work correctly."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with patch("redis.RedisCluster") as mock_redis_cluster:
            mock_instance = Mock()
            mock_instance.ping.return_value = True
            mock_instance.set.return_value = True
            mock_instance.get.return_value = "test_value"
            mock_redis_cluster.return_value = mock_instance

            client = ClusterRedisClient(config)
            redis_client = client.create_connection()

            # Test basic operations
            assert redis_client.ping() is True
            assert redis_client.set("test_key", "test_value") is True
            assert redis_client.get("test_key") == "test_value"

    def test_connection_error_handling(self):
        """Test that connection errors are handled properly."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with patch("redis.RedisCluster") as mock_redis_cluster:
            mock_redis_cluster.side_effect = Exception("Connection failed")

            client = ClusterRedisClient(config)

            with pytest.raises(Exception, match="Connection failed"):
                client.create_connection()

    def test_client_repr(self):
        """Test that client has a meaningful string representation."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
        )
        client = ClusterRedisClient(config)
        repr_str = repr(client)
        assert "ClusterRedisClient" in repr_str
        assert "localhost:7000" in repr_str
        assert "CLUSTER" in repr_str

    def test_cluster_nodes_parsing(self):
        """Test that cluster nodes are properly parsed from strings."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001", "node3:7002"],
        )

        with patch("redis.RedisCluster") as mock_redis_cluster:
            mock_instance = Mock()
            mock_redis_cluster.return_value = mock_instance

            client = ClusterRedisClient(config)
            client.create_connection()

            # Verify cluster nodes were parsed correctly
            call_args = mock_redis_cluster.call_args[1]
            startup_nodes = call_args["startup_nodes"]
            assert len(startup_nodes) == 3
            # Check that ClusterNode objects were created with correct host/port
            assert startup_nodes[0].host == "node1"
            assert startup_nodes[0].port == 7000
            assert startup_nodes[1].host == "node2"
            assert startup_nodes[1].port == 7001
            assert startup_nodes[2].host == "node3"
            assert startup_nodes[2].port == 7002

    def test_create_async_cluster_connection(self):
        """Test that async Cluster connection is created with correct parameters."""
        config = RedisConnectionConfig(
            host="localhost",
            port=7000,
            password="secret",
            mode=RedisConnectionMode.CLUSTER,
            cluster_nodes=["node1:7000", "node2:7001"],
        )

        with patch("redis.asyncio.RedisCluster") as mock_redis_cluster:
            mock_instance = Mock()
            mock_redis_cluster.return_value = mock_instance

            client = ClusterRedisClient(config, async_client=True)
            client.create_connection()

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
