"""
Unit tests for async Redis clients.

This module tests the async Redis client wrappers for different deployment modes.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from python_redis_factory.clients.cluster import ClusterRedisClient
from python_redis_factory.clients.sentinel import SentinelRedisClient
from python_redis_factory.clients.standalone import StandaloneRedisClient
from python_redis_factory.interfaces import RedisConnectionConfig, RedisConnectionMode


class TestAsyncStandaloneRedisClient:
    """Test the async standalone Redis client functionality."""

    @pytest.mark.asyncio
    async def test_create_async_standalone_connection(self):
        """Test that async standalone connection is created with correct parameters."""
        config = RedisConnectionConfig(
            host="localhost",
            port=6379,
            password="secret",
            mode=RedisConnectionMode.STANDALONE,
            ssl=True,
            ssl_cert_reqs="required",
        )

        with patch(
            "python_redis_factory.clients.standalone.redis.asyncio.Redis.from_pool"
        ) as mock_from_pool:
            mock_instance = AsyncMock()
            mock_from_pool.return_value = mock_instance

            StandaloneRedisClient.create(config, async_client=True)

            mock_from_pool.assert_called_once()


class TestAsyncSentinelRedisClient:
    """Test the async Sentinel Redis client functionality."""

    @pytest.mark.asyncio
    async def test_create_async_sentinel_connection(self):
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

            SentinelRedisClient.create(config, async_client=True)

            mock_sentinel.assert_called_once()
            call_args = mock_sentinel.call_args[1]

            assert call_args["password"] == "secret"
            assert call_args["ssl"] is True
            assert call_args["ssl_cert_reqs"] == "required"
            assert call_args["decode_responses"] is True


class TestAsyncClusterRedisClient:
    """Test the async Cluster Redis client functionality."""

    @pytest.mark.asyncio
    async def test_create_async_cluster_connection(self):
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

        with patch(
            "python_redis_factory.clients.cluster.AsyncRedisCluster"
        ) as mock_redis_cluster:
            mock_instance = AsyncMock()
            mock_redis_cluster.return_value = mock_instance

            ClusterRedisClient.create(config, async_client=True)

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
            assert call_args["decode_responses"] is True
