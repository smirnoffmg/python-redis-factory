"""
Unit tests for the standalone Redis client.

This module tests the standalone Redis client creation and basic operations.
"""

from unittest.mock import Mock, patch

import pytest

from python_redis_factory.clients.standalone import StandaloneRedisClient
from python_redis_factory.interfaces import RedisConnectionConfig, RedisConnectionMode


class TestStandaloneRedisClient:
    """Test the standalone Redis client functionality."""

    @pytest.mark.asyncio
    @patch("python_redis_factory.clients.standalone.redis.Redis.from_pool")
    async def test_create_redis_connection(self, mock_from_pool):
        """Test that Redis connection is created with correct parameters."""
        mock_redis_instance = Mock()
        mock_from_pool.return_value = mock_redis_instance

        config = RedisConnectionConfig(
            host="redis.example.com",
            port=6380,
            password="secret",
            db=1,
            max_connections=20,
            socket_timeout=10.0,
            socket_connect_timeout=3.0,
        )

        redis_client = await StandaloneRedisClient.create(config)

        mock_from_pool.assert_called_once()
        assert redis_client == mock_redis_instance

    @pytest.mark.asyncio
    @patch("python_redis_factory.clients.standalone.redis.Redis.from_pool")
    async def test_create_redis_connection_with_ssl(self, mock_from_pool):
        """Test that Redis connection is created with SSL parameters."""
        mock_redis_instance = Mock()
        mock_from_pool.return_value = mock_redis_instance

        config = RedisConnectionConfig(
            host="redis.example.com",
            port=6380,
            ssl=True,
            ssl_cert_reqs="required",
            ssl_ca_certs="/path/to/ca.crt",
        )

        await StandaloneRedisClient.create(config)

        mock_from_pool.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_config_wrong_mode(self):
        """Test that client rejects configuration with wrong mode."""
        config = RedisConnectionConfig(
            host="localhost",
            mode=RedisConnectionMode.SENTINEL,  # Wrong mode
        )

        with pytest.raises(
            ValueError, match="Configuration must be for STANDALONE mode"
        ):
            await StandaloneRedisClient.create(config)

    @pytest.mark.asyncio
    @patch("python_redis_factory.clients.standalone.redis.Redis.from_pool")
    async def test_basic_redis_operations(self, mock_from_pool):
        """Test basic Redis operations work correctly."""
        mock_redis_instance = Mock()
        mock_from_pool.return_value = mock_redis_instance

        # Setup mock responses
        mock_redis_instance.set.return_value = True
        mock_redis_instance.get.return_value = "test_value"
        mock_redis_instance.ping.return_value = True

        config = RedisConnectionConfig(
            host="localhost", mode=RedisConnectionMode.STANDALONE
        )

        redis_client = await StandaloneRedisClient.create(config)

        # Test basic operations
        assert redis_client.set("test_key", "test_value") is True
        assert redis_client.get("test_key") == "test_value"
        assert redis_client.ping() is True

        # Verify methods were called
        redis_client.set.assert_called_once_with("test_key", "test_value")
        redis_client.get.assert_called_once_with("test_key")
        redis_client.ping.assert_called_once()

    @pytest.mark.asyncio
    @patch("python_redis_factory.clients.standalone.redis.ConnectionPool")
    async def test_connection_error_handling(self, mock_connection_pool):
        """Test that connection errors are handled properly."""
        from redis.exceptions import ConnectionError

        # Make ConnectionPool constructor raise an error
        mock_connection_pool.side_effect = ConnectionError("Connection failed")

        config = RedisConnectionConfig(
            host="invalid-host", mode=RedisConnectionMode.STANDALONE
        )

        with pytest.raises(ConnectionError, match="Connection failed"):
            await StandaloneRedisClient.create(config)
