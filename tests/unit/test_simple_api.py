"""
Unit tests for the simplified API.

This module tests the get_redis_client function that provides a simple one-liner
way to create Redis clients from connection strings.
"""

from unittest.mock import Mock, patch

import pytest

from python_redis_factory import get_redis_client


class TestGetRedisClient:
    """Test the get_redis_client function."""

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_get_redis_client_standalone_basic(self, mock_redis_class):
        """Test creating a standalone Redis client with basic URI."""
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance

        client = get_redis_client("redis://localhost:6379")

        assert client == mock_redis_instance
        mock_redis_class.assert_called_once()
        call_args = mock_redis_class.call_args[1]
        assert call_args["host"] == "localhost"
        assert call_args["port"] == 6379
        assert call_args["password"] is None
        assert call_args["db"] == 0

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_get_redis_client_standalone_with_password(self, mock_redis_class):
        """Test creating a standalone Redis client with password."""
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance

        client = get_redis_client("redis://:secret@localhost:6379")

        assert client == mock_redis_instance
        mock_redis_class.assert_called_once()
        call_args = mock_redis_class.call_args[1]
        assert call_args["password"] == "secret"

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_get_redis_client_standalone_with_db(self, mock_redis_class):
        """Test creating a standalone Redis client with database selection."""
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance

        client = get_redis_client("redis://localhost:6379/5")

        assert client == mock_redis_instance
        mock_redis_class.assert_called_once()
        call_args = mock_redis_class.call_args[1]
        assert call_args["db"] == 5

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_get_redis_client_standalone_with_ssl(self, mock_redis_class):
        """Test creating a standalone Redis client with SSL."""
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance

        client = get_redis_client("rediss://localhost:6379")

        assert client == mock_redis_instance
        mock_redis_class.assert_called_once()
        call_args = mock_redis_class.call_args[1]
        assert call_args["ssl"] is True

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_get_redis_client_standalone_complex(self, mock_redis_class):
        """Test creating a standalone Redis client with complex configuration."""
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance

        client = get_redis_client("redis://user:pass@redis.example.com:6380/2")

        assert client == mock_redis_instance
        mock_redis_class.assert_called_once()
        call_args = mock_redis_class.call_args[1]
        assert call_args["host"] == "redis.example.com"
        assert call_args["port"] == 6380
        assert call_args["password"] == "pass"
        assert call_args["db"] == 2

    @patch("python_redis_factory.clients.sentinel.redis.sentinel.Sentinel")
    def test_get_redis_client_sentinel(self, mock_sentinel_class):
        """Test creating a Sentinel Redis client through the simple API."""
        mock_sentinel_instance = Mock()
        mock_sentinel_class.return_value = mock_sentinel_instance
        mock_master_client = Mock()
        mock_sentinel_instance.master_for.return_value = mock_master_client

        client = get_redis_client("redis+sentinel://sentinel1:26379/mymaster")

        assert client == mock_master_client
        mock_sentinel_class.assert_called_once()

    @patch("python_redis_factory.clients.cluster.redis.RedisCluster")
    def test_get_redis_client_cluster(self, mock_redis_cluster_class):
        """Test creating a Cluster Redis client through the simple API."""
        mock_redis_instance = Mock()
        mock_redis_cluster_class.return_value = mock_redis_instance

        client = get_redis_client("redis+cluster://node1:7000,node2:7001")

        assert client == mock_redis_instance
        mock_redis_cluster_class.assert_called_once()
        call_args = mock_redis_cluster_class.call_args[1]
        assert "startup_nodes" in call_args
        assert len(call_args["startup_nodes"]) == 2
        # Check that ClusterNode objects were created with correct host/port
        assert call_args["startup_nodes"][0].host == "node1"
        assert call_args["startup_nodes"][0].port == 7000
        assert call_args["startup_nodes"][1].host == "node2"
        assert call_args["startup_nodes"][1].port == 7001

    def test_get_redis_client_invalid_uri(self):
        """Test that invalid URI raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Redis URI scheme: invalid"):
            get_redis_client("invalid://uri")

    def test_get_redis_client_empty_uri(self):
        """Test that empty URI raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Redis URI format"):
            get_redis_client("")

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_get_redis_client_basic_operations(self, mock_redis_class):
        """Test that the returned client supports basic Redis operations."""
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.set.return_value = True
        mock_redis_instance.get.return_value = "test_value"

        client = get_redis_client("redis://localhost:6379")

        # Test basic operations work
        assert client.ping() is True
        assert client.set("key", "value") is True
        assert client.get("key") == "test_value"

        # Verify methods were called
        client.ping.assert_called_once()
        client.set.assert_called_once_with("key", "value")
        client.get.assert_called_once_with("key")

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_get_redis_client_connection_error(self, mock_redis_class):
        """Test that connection errors are properly propagated."""
        from redis.exceptions import ConnectionError

        mock_redis_class.side_effect = ConnectionError("Connection failed")

        with pytest.raises(ConnectionError, match="Connection failed"):
            get_redis_client("redis://invalid-host:6379")
