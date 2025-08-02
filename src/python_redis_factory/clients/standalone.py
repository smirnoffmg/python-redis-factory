"""
Standalone Redis client implementation.

This module provides the StandaloneRedisClient class for connecting to
single Redis instances in both sync and async modes.
"""

import redis
import redis.asyncio

from ..interfaces import RedisClient, RedisConnectionConfig, RedisConnectionMode


class StandaloneRedisClient:
    """A builder for creating standalone Redis clients."""

    @staticmethod
    async def create(
        config: RedisConnectionConfig, async_client: bool = False
    ) -> RedisClient:
        """
        Create a Redis connection based on the configuration.

        Args:
            config: Redis connection configuration.
            async_client: If True, creates an async Redis client.

        Returns:
            A Redis client instance.

        Raises:
            ValueError: If the configuration mode is not STANDALONE.
            redis.ConnectionError: If the connection cannot be established.
        """
        if config.mode != RedisConnectionMode.STANDALONE:
            raise ValueError("Configuration must be for STANDALONE mode")

        # Build connection parameters
        connection_params = {
            "host": config.host,
            "port": config.port,
            "decode_responses": True,
        }

        # Add optional parameters (include None values for testing consistency)
        connection_params["password"] = config.password

        if config.db is not None:
            connection_params["db"] = config.db

        if config.max_connections:
            connection_params["max_connections"] = config.max_connections

        if config.socket_timeout:
            connection_params["socket_timeout"] = config.socket_timeout

        if config.socket_connect_timeout:
            connection_params["socket_connect_timeout"] = (
                config.socket_connect_timeout
            )

        # SSL parameters
        if config.ssl:
            connection_params["ssl"] = True
            if config.ssl_cert_reqs:
                connection_params["ssl_cert_reqs"] = config.ssl_cert_reqs
            if config.ssl_ca_certs:
                connection_params["ssl_ca_certs"] = config.ssl_ca_certs

        # Create appropriate Redis client
        if async_client:
            return redis.asyncio.Redis.from_pool(
                redis.asyncio.ConnectionPool(**connection_params)
            )
        else:
            return redis.Redis.from_pool(redis.ConnectionPool(**connection_params))
