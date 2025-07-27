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

    def test_create_standalone_client(self):
        """Test creating a standalone Redis client."""
        config = RedisConnectionConfig(
            host="localhost", port=6379, mode=RedisConnectionMode.STANDALONE
        )

        client = StandaloneRedisClient(config)

        assert client.config == config
        assert client.config.mode == RedisConnectionMode.STANDALONE

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_create_redis_connection(self, mock_redis_class):
        """Test that Redis connection is created with correct parameters."""
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance

        config = RedisConnectionConfig(
            host="redis.example.com",
            port=6380,
            password="secret",
            db=1,
            max_connections=20,
            socket_timeout=10.0,
            socket_connect_timeout=3.0,
        )

        client = StandaloneRedisClient(config)
        redis_client = client.create_connection()

        # Verify Redis was called with correct parameters
        mock_redis_class.assert_called_once_with(
            host="redis.example.com",
            port=6380,
            password="secret",
            db=1,
            max_connections=20,
            socket_timeout=10.0,
            socket_connect_timeout=3.0,
            decode_responses=True,
            ssl=False,
        )

        assert redis_client == mock_redis_instance

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_create_redis_connection_with_ssl(self, mock_redis_class):
        """Test that Redis connection is created with SSL parameters."""
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance

        config = RedisConnectionConfig(
            host="redis.example.com",
            port=6380,
            ssl=True,
            ssl_cert_reqs="required",
            ssl_ca_certs="/path/to/ca.crt",
        )

        client = StandaloneRedisClient(config)
        client.create_connection()

        # Verify SSL parameters were passed
        mock_redis_class.assert_called_once()
        call_args = mock_redis_class.call_args[1]
        assert call_args["ssl"] is True
        assert call_args["ssl_cert_reqs"] == "required"
        assert call_args["ssl_ca_certs"] == "/path/to/ca.crt"

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_create_redis_connection_defaults(self, mock_redis_class):
        """Test that Redis connection uses default values when not specified."""
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance

        config = RedisConnectionConfig(
            host="localhost", mode=RedisConnectionMode.STANDALONE
        )

        client = StandaloneRedisClient(config)
        client.create_connection()

        # Verify default values were used
        mock_redis_class.assert_called_once()
        call_args = mock_redis_class.call_args[1]
        assert call_args["host"] == "localhost"
        assert call_args["port"] == 6379
        assert call_args["password"] is None
        assert call_args["db"] == 0
        assert call_args["max_connections"] == 10
        assert call_args["socket_timeout"] == 5.0
        assert call_args["socket_connect_timeout"] == 5.0
        assert call_args["ssl"] is False
        assert call_args["decode_responses"] is True

    def test_validate_config_wrong_mode(self):
        """Test that client rejects configuration with wrong mode."""
        config = RedisConnectionConfig(
            host="localhost",
            mode=RedisConnectionMode.SENTINEL,  # Wrong mode
        )

        with pytest.raises(
            ValueError, match="Configuration must be for STANDALONE mode"
        ):
            StandaloneRedisClient(config)

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_basic_redis_operations(self, mock_redis_class):
        """Test basic Redis operations work correctly."""
        mock_redis_instance = Mock()
        mock_redis_class.return_value = mock_redis_instance

        # Setup mock responses
        mock_redis_instance.set.return_value = True
        mock_redis_instance.get.return_value = "test_value"
        mock_redis_instance.ping.return_value = True

        config = RedisConnectionConfig(
            host="localhost", mode=RedisConnectionMode.STANDALONE
        )

        client = StandaloneRedisClient(config)
        redis_client = client.create_connection()

        # Test basic operations
        assert redis_client.set("test_key", "test_value") is True
        assert redis_client.get("test_key") == "test_value"
        assert redis_client.ping() is True

        # Verify methods were called
        redis_client.set.assert_called_once_with("test_key", "test_value")
        redis_client.get.assert_called_once_with("test_key")
        redis_client.ping.assert_called_once()

    @patch("python_redis_factory.clients.standalone.redis.Redis")
    def test_connection_error_handling(self, mock_redis_class):
        """Test that connection errors are handled properly."""
        from redis.exceptions import ConnectionError

        # Make Redis constructor raise an error
        mock_redis_class.side_effect = ConnectionError("Connection failed")

        config = RedisConnectionConfig(
            host="invalid-host", mode=RedisConnectionMode.STANDALONE
        )

        client = StandaloneRedisClient(config)

        with pytest.raises(ConnectionError, match="Connection failed"):
            client.create_connection()

    def test_client_repr(self):
        """Test that client has a meaningful string representation."""
        config = RedisConnectionConfig(
            host="localhost", port=6379, mode=RedisConnectionMode.STANDALONE
        )

        client = StandaloneRedisClient(config)
        repr_str = repr(client)

        assert "StandaloneRedisClient" in repr_str
        assert "localhost:6379" in repr_str
