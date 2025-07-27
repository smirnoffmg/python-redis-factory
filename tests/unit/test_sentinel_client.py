"""
Unit tests for the Sentinel Redis client.

This module tests the Sentinel Redis client creation and basic operations.
"""

from unittest.mock import Mock, patch

import pytest

from python_redis_factory.clients.sentinel import SentinelRedisClient
from python_redis_factory.interfaces import RedisConnectionConfig, RedisConnectionMode


class TestSentinelRedisClient:
    """Test the Sentinel Redis client functionality."""

    def test_create_sentinel_client(self):
        """Test creating a Sentinel Redis client."""
        config = RedisConnectionConfig(
            host="sentinel1",
            port=26379,
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379", "sentinel2:26379"],
            service_name="mymaster",
        )

        client = SentinelRedisClient(config)

        assert client.config == config
        assert client.config.mode == RedisConnectionMode.SENTINEL
        assert client.config.sentinel_hosts == ["sentinel1:26379", "sentinel2:26379"]
        assert client.config.service_name == "mymaster"

    @patch("python_redis_factory.clients.sentinel.redis.sentinel.Sentinel")
    def test_create_sentinel_connection(self, mock_sentinel_class):
        """Test that Sentinel connection is created with correct parameters."""
        mock_sentinel_instance = Mock()
        mock_sentinel_class.return_value = mock_sentinel_instance
        mock_master_client = Mock()
        mock_sentinel_instance.master_for.return_value = mock_master_client

        config = RedisConnectionConfig(
            host="sentinel1",
            port=26379,
            password="secret",
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379", "sentinel2:26379"],
            service_name="mymaster",
            max_connections=20,
            socket_timeout=10.0,
            socket_connect_timeout=3.0,
        )

        client = SentinelRedisClient(config)
        redis_client = client.create_connection()

        # Verify Sentinel was called with correct parameters
        mock_sentinel_class.assert_called_once_with(
            [("sentinel1", 26379), ("sentinel2", 26379)],
            password="secret",
            max_connections=20,
            socket_timeout=10.0,
            socket_connect_timeout=3.0,
            decode_responses=True,
            ssl=False,
        )

        # Verify master_for was called with service name
        mock_sentinel_instance.master_for.assert_called_once_with("mymaster")
        assert redis_client == mock_master_client

    @patch("python_redis_factory.clients.sentinel.redis.sentinel.Sentinel")
    def test_create_sentinel_connection_with_ssl(self, mock_sentinel_class):
        """Test that Sentinel connection is created with SSL parameters."""
        mock_sentinel_instance = Mock()
        mock_sentinel_class.return_value = mock_sentinel_instance
        mock_master_client = Mock()
        mock_sentinel_instance.master_for.return_value = mock_master_client

        config = RedisConnectionConfig(
            host="sentinel1",
            port=26379,
            mode=RedisConnectionMode.SENTINEL,
            ssl=True,
            ssl_cert_reqs="required",
            ssl_ca_certs="/path/to/ca.crt",
            sentinel_hosts=["sentinel1:26379"],
            service_name="mymaster",
        )

        client = SentinelRedisClient(config)
        client.create_connection()

        # Verify SSL parameters were passed
        mock_sentinel_class.assert_called_once()
        call_args = mock_sentinel_class.call_args[1]
        assert call_args["ssl"] is True
        assert call_args["ssl_cert_reqs"] == "required"
        assert call_args["ssl_ca_certs"] == "/path/to/ca.crt"

    @patch("python_redis_factory.clients.sentinel.redis.sentinel.Sentinel")
    def test_create_sentinel_connection_defaults(self, mock_sentinel_class):
        """Test that Sentinel connection uses default values when not specified."""
        mock_sentinel_instance = Mock()
        mock_sentinel_class.return_value = mock_sentinel_instance
        mock_master_client = Mock()
        mock_sentinel_instance.master_for.return_value = mock_master_client

        config = RedisConnectionConfig(
            host="sentinel1",
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379"],
            service_name="mymaster",
        )

        client = SentinelRedisClient(config)
        client.create_connection()

        # Verify default values were used
        mock_sentinel_class.assert_called_once()
        call_args = mock_sentinel_class.call_args[1]
        assert call_args["password"] is None
        assert call_args["max_connections"] == 10
        assert call_args["socket_timeout"] == 5.0
        assert call_args["socket_connect_timeout"] == 5.0
        assert call_args["ssl"] is False
        assert call_args["decode_responses"] is True

    def test_validate_config_wrong_mode(self):
        """Test that client rejects configuration with wrong mode."""
        config = RedisConnectionConfig(
            host="localhost",
            mode=RedisConnectionMode.STANDALONE,  # Wrong mode
        )

        with pytest.raises(ValueError, match="Configuration must be for SENTINEL mode"):
            SentinelRedisClient(config)

    def test_validate_config_missing_sentinel_hosts(self):
        """Test that client rejects configuration without sentinel hosts."""
        config = RedisConnectionConfig(
            host="sentinel1",
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=None,  # Missing sentinel hosts
            service_name="mymaster",
        )

        with pytest.raises(
            ValueError, match="Sentinel hosts are required for Sentinel mode"
        ):
            SentinelRedisClient(config)

    def test_validate_config_missing_service_name(self):
        """Test that client rejects configuration without service name."""
        config = RedisConnectionConfig(
            host="sentinel1",
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379"],
            service_name=None,  # Missing service name
        )

        with pytest.raises(
            ValueError, match="Service name is required for Sentinel mode"
        ):
            SentinelRedisClient(config)

    @patch("python_redis_factory.clients.sentinel.redis.sentinel.Sentinel")
    def test_basic_redis_operations(self, mock_sentinel_class):
        """Test basic Redis operations work correctly."""
        mock_sentinel_instance = Mock()
        mock_sentinel_class.return_value = mock_sentinel_instance
        mock_master_client = Mock()
        mock_sentinel_instance.master_for.return_value = mock_master_client

        # Setup mock responses
        mock_master_client.set.return_value = True
        mock_master_client.get.return_value = "test_value"
        mock_master_client.ping.return_value = True

        config = RedisConnectionConfig(
            host="sentinel1",
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379"],
            service_name="mymaster",
        )

        client = SentinelRedisClient(config)
        redis_client = client.create_connection()

        # Test basic operations
        assert redis_client.set("test_key", "test_value") is True
        assert redis_client.get("test_key") == "test_value"
        assert redis_client.ping() is True

        # Verify methods were called
        redis_client.set.assert_called_once_with("test_key", "test_value")
        redis_client.get.assert_called_once_with("test_key")
        redis_client.ping.assert_called_once()

    @patch("python_redis_factory.clients.sentinel.redis.sentinel.Sentinel")
    def test_connection_error_handling(self, mock_sentinel_class):
        """Test that connection errors are handled properly."""
        from redis.exceptions import ConnectionError

        # Make Sentinel constructor raise an error
        mock_sentinel_class.side_effect = ConnectionError("Sentinel connection failed")

        config = RedisConnectionConfig(
            host="invalid-sentinel",
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["invalid-sentinel:26379"],
            service_name="mymaster",
        )

        client = SentinelRedisClient(config)

        with pytest.raises(ConnectionError, match="Sentinel connection failed"):
            client.create_connection()

    def test_client_repr(self):
        """Test that client has a meaningful string representation."""
        config = RedisConnectionConfig(
            host="sentinel1",
            port=26379,
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379", "sentinel2:26379"],
            service_name="mymaster",
        )

        client = SentinelRedisClient(config)
        repr_str = repr(client)

        assert "SentinelRedisClient" in repr_str
        assert "mymaster" in repr_str
        assert "sentinel1:26379" in repr_str

    @patch("python_redis_factory.clients.sentinel.redis.sentinel.Sentinel")
    def test_sentinel_host_parsing(self, mock_sentinel_class):
        """Test that sentinel hosts are properly parsed from strings."""
        mock_sentinel_instance = Mock()
        mock_sentinel_class.return_value = mock_sentinel_instance
        mock_master_client = Mock()
        mock_sentinel_instance.master_for.return_value = mock_master_client

        config = RedisConnectionConfig(
            host="sentinel1",
            mode=RedisConnectionMode.SENTINEL,
            sentinel_hosts=["sentinel1:26379", "sentinel2:26380", "sentinel3:26381"],
            service_name="mymaster",
        )

        client = SentinelRedisClient(config)
        client.create_connection()

        # Verify sentinel hosts were parsed correctly
        mock_sentinel_class.assert_called_once()
        sentinel_hosts = mock_sentinel_class.call_args[0][
            0
        ]  # First positional argument
        assert sentinel_hosts == [
            ("sentinel1", 26379),
            ("sentinel2", 26380),
            ("sentinel3", 26381),
        ]
