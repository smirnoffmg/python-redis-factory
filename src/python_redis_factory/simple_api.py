"""
Simple API for python-redis-factory.

This module provides a simplified interface for creating Redis clients
with minimal configuration.
"""

from .clients.cluster import ClusterRedisClient
from .clients.sentinel import SentinelRedisClient
from .clients.standalone import StandaloneRedisClient
from .factory import RedisClientFactory
from .interfaces import RedisClient, RedisConnectionMode
from .uri_parser import parse_redis_uri

# Global factory instance
_redis_client_factory = RedisClientFactory()
_redis_client_factory.register_builder(
    RedisConnectionMode.STANDALONE, StandaloneRedisClient.create
)
_redis_client_factory.register_builder(
    RedisConnectionMode.SENTINEL, SentinelRedisClient.create
)
_redis_client_factory.register_builder(
    RedisConnectionMode.CLUSTER, ClusterRedisClient.create
)


def get_redis_client(redis_dsn: str, async_client: bool = False) -> RedisClient:
    """
    Create a Redis client from a connection string.

    This is the main entry point for the library, providing a simple
    one-liner way to create Redis clients (both sync and async).

    Args:
        redis_dsn: Redis connection string (URI format)
        async_client: If True, returns an async Redis client. If False, returns a sync client.

    Returns:
        A Redis client instance (sync or async based on async_client parameter)

    Raises:
        ValueError: If the connection string is invalid
        NotImplementedError: If the connection mode is not yet supported
        ConnectionError: If connection cannot be established

    Examples:
        >>> # Sync Standalone Redis
        >>> client = get_redis_client("redis://localhost:6379")
        >>>
        >>> # Async Standalone Redis
        >>> client = get_redis_client("redis://localhost:6379", async_client=True)
        >>>
        >>> # Sync with password
        >>> client = get_redis_client("redis://:secret@localhost:6379")
        >>>
        >>> # Async with password
        >>> client = get_redis_client("redis://:secret@localhost:6379", async_client=True)
        >>>
        >>> # Sync with database selection
        >>> client = get_redis_client("redis://localhost:6379/1")
        >>>
        >>> # Async with SSL
        >>> client = get_redis_client("rediss://localhost:6379", async_client=True)
        >>>
        >>> # Sync Sentinel
        >>> client = get_redis_client("redis+sentinel://sentinel1:26379/mymaster")
        >>>
        >>> # Async Cluster
        >>> client = get_redis_client("redis+cluster://node1:7000,node2:7001", async_client=True)
    """
    if not redis_dsn:
        raise ValueError("Invalid Redis URI format")

    config = parse_redis_uri(redis_dsn)
    if async_client:
        return _redis_client_factory.create_client(config, async_client=True)
    else:
        import asyncio

        return asyncio.run(
            _redis_client_factory.create_client(config, async_client=False)
        )
