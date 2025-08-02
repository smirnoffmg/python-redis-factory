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

    @pytest.mark.asyncio
    @patch("python_redis_factory.simple_api._redis_client_factory.create_client")
    async def test_get_redis_client_standalone(self, mock_create_client):
        """Test creating a standalone Redis client with various URIs."""
        mock_redis_instance = Mock()
        mock_create_client.return_value = mock_redis_instance

        # Test basic URI
        client = await get_redis_client("redis://localhost:6379", async_client=False)
        assert client == mock_redis_instance

        # Test with password
        client = await get_redis_client(
            "redis://:secret@localhost:6379", async_client=False
        )
        assert client == mock_redis_instance

        # Test with database
        client = await get_redis_client("redis://localhost:6379/5", async_client=False)
        assert client == mock_redis_instance

        # Test with SSL
        client = await get_redis_client("rediss://localhost:6379", async_client=False)
        assert client == mock_redis_instance

    @pytest.mark.asyncio
    @patch("python_redis_factory.simple_api._redis_client_factory.create_client")
    async def test_get_redis_client_sentinel(self, mock_create_client):
        """Test creating a Sentinel Redis client through the simple API."""
        mock_master_client = Mock()
        mock_create_client.return_value = mock_master_client

        client = await get_redis_client(
            "redis+sentinel://sentinel1:26379/mymaster", async_client=False
        )

        assert client == mock_master_client
        mock_create_client.assert_called_once()

    @pytest.mark.asyncio
    @patch("python_redis_factory.simple_api._redis_client_factory.create_client")
    async def test_get_redis_client_cluster(self, mock_create_client):
        """Test creating a Cluster Redis client through the simple API."""
        mock_redis_instance = Mock()
        mock_create_client.return_value = mock_redis_instance

        client = await get_redis_client(
            "redis+cluster://node1:7000,node2:7001", async_client=False
        )

        assert client == mock_redis_instance
        mock_create_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_redis_client_invalid_uri(self):
        """Test that invalid URI raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Redis URI scheme: invalid"):
            await get_redis_client("invalid://uri", async_client=False)

    @pytest.mark.asyncio
    async def test_get_redis_client_empty_uri(self):
        """Test that empty URI raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Redis URI format"):
            await get_redis_client("", async_client=False)

    @pytest.mark.asyncio
    @patch("python_redis_factory.simple_api._redis_client_factory.create_client")
    async def test_get_redis_client_basic_operations(self, mock_create_client):
        """Test that the returned client supports basic Redis operations."""
        mock_redis_instance = Mock()
        mock_create_client.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.set.return_value = True
        mock_redis_instance.get.return_value = "test_value"

        client = await get_redis_client("redis://localhost:6379", async_client=False)

        # Test basic operations work
        assert client.ping() is True
        assert client.set("key", "value") is True
        assert client.get("key") == "test_value"

        # Verify methods were called
        client.ping.assert_called_once()
        client.set.assert_called_once_with("key", "value")
        client.get.assert_called_once_with("key")

    @pytest.mark.asyncio
    @patch("python_redis_factory.simple_api.parse_redis_uri")
    async def test_get_redis_client_connection_error(self, mock_parse_uri):
        """Test that connection errors are properly propagated."""
        from redis.exceptions import ConnectionError

        mock_parse_uri.side_effect = ConnectionError("Connection failed")

        with pytest.raises(ConnectionError, match="Connection failed"):
            await get_redis_client("redis://invalid-host:6379", async_client=False)
