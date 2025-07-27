"""
Unit tests for the URI parser module.

This module tests the Redis URI parsing functionality.
"""

import pytest

from python_redis_factory.interfaces import RedisConnectionMode
from python_redis_factory.uri_parser import parse_redis_uri


class TestURIParser:
    """Test the Redis URI parser functionality."""

    def test_parse_standalone_uri_basic(self):
        """Test parsing a basic standalone Redis URI."""
        uri = "redis://localhost:6379"
        config = parse_redis_uri(uri)

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.password is None
        assert config.db == 0
        assert config.mode == RedisConnectionMode.STANDALONE

    def test_parse_standalone_uri_with_password(self):
        """Test parsing a standalone Redis URI with password."""
        uri = "redis://:password@localhost:6379"
        config = parse_redis_uri(uri)

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.password == "password"
        assert config.db == 0
        assert config.mode == RedisConnectionMode.STANDALONE

    def test_parse_standalone_uri_with_db(self):
        """Test parsing a standalone Redis URI with database selection."""
        uri = "redis://localhost:6379/1"
        config = parse_redis_uri(uri)

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.password is None
        assert config.db == 1
        assert config.mode == RedisConnectionMode.STANDALONE

    def test_parse_standalone_uri_with_password_and_db(self):
        """Test parsing a standalone Redis URI with password and database."""
        uri = "redis://:password@localhost:6379/2"
        config = parse_redis_uri(uri)

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.password == "password"
        assert config.db == 2
        assert config.mode == RedisConnectionMode.STANDALONE

    def test_parse_standalone_uri_with_username_and_password(self):
        """Test parsing a standalone Redis URI with username and password."""
        uri = "redis://user:password@localhost:6379"
        config = parse_redis_uri(uri)

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.password == "password"
        assert config.db == 0
        assert config.mode == RedisConnectionMode.STANDALONE

    def test_parse_sentinel_uri(self):
        """Test parsing a Sentinel Redis URI."""
        uri = "redis+sentinel://sentinel1:26379,sentinel2:26379/mymaster"
        config = parse_redis_uri(uri)

        assert config.mode == RedisConnectionMode.SENTINEL
        assert config.sentinel_hosts == ["sentinel1:26379", "sentinel2:26379"]
        assert config.service_name == "mymaster"
        assert config.host == "sentinel1"  # Default to first sentinel
        assert config.port == 26379

    def test_parse_sentinel_uri_with_password(self):
        """Test parsing a Sentinel Redis URI with password."""
        uri = "redis+sentinel://:password@sentinel1:26379,sentinel2:26379/mymaster"
        config = parse_redis_uri(uri)

        assert config.mode == RedisConnectionMode.SENTINEL
        assert config.sentinel_hosts == ["sentinel1:26379", "sentinel2:26379"]
        assert config.service_name == "mymaster"
        assert config.sentinel_password == "password"

    def test_parse_cluster_uri(self):
        """Test parsing a Cluster Redis URI."""
        uri = "redis+cluster://node1:7000,node2:7001,node3:7002"
        config = parse_redis_uri(uri)

        assert config.mode == RedisConnectionMode.CLUSTER
        assert config.cluster_nodes == ["node1:7000", "node2:7001", "node3:7002"]
        assert config.host == "node1"  # Default to first node
        assert config.port == 7000

    def test_parse_cluster_uri_with_password(self):
        """Test parsing a Cluster Redis URI with password."""
        uri = "redis+cluster://:password@node1:7000,node2:7001"
        config = parse_redis_uri(uri)

        assert config.mode == RedisConnectionMode.CLUSTER
        assert config.cluster_nodes == ["node1:7000", "node2:7001"]
        assert config.password == "password"

    def test_parse_invalid_uri_scheme(self):
        """Test that invalid URI schemes raise an error."""
        with pytest.raises(ValueError, match="Invalid Redis URI scheme"):
            parse_redis_uri("http://localhost:6379")

    def test_parse_invalid_uri_format(self):
        """Test that malformed URIs raise an error."""
        with pytest.raises(ValueError, match="Invalid Redis URI format"):
            parse_redis_uri("redis://")

    def test_parse_uri_with_invalid_port(self):
        """Test that URIs with invalid ports raise an error."""
        with pytest.raises(ValueError, match="Invalid port number"):
            parse_redis_uri("redis://localhost:99999")

    def test_parse_uri_with_invalid_db(self):
        """Test that URIs with invalid database numbers raise an error."""
        with pytest.raises(ValueError, match="Invalid database number"):
            parse_redis_uri("redis://localhost:6379/-1")

    def test_parse_sentinel_uri_missing_service_name(self):
        """Test that Sentinel URIs without service name raise an error."""
        with pytest.raises(ValueError, match="Sentinel URI must include service name"):
            parse_redis_uri("redis+sentinel://sentinel1:26379")

    def test_parse_cluster_uri_missing_nodes(self):
        """Test that Cluster URIs without nodes raise an error."""
        with pytest.raises(
            ValueError, match="Cluster URI must include at least one node"
        ):
            parse_redis_uri("redis+cluster://")

    def test_parse_uri_with_ssl(self):
        """Test parsing a Redis URI with SSL enabled."""
        uri = "rediss://localhost:6379"
        config = parse_redis_uri(uri)

        assert config.host == "localhost"
        assert config.port == 6379
        assert config.ssl is True
        assert config.mode == RedisConnectionMode.STANDALONE
