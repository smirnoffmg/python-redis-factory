"""
Standalone Redis client implementation.

This module provides the StandaloneRedisClient class for connecting to
single Redis instances in both sync and async modes.
"""

import redis
import redis.asyncio

from ..interfaces import RedisConnectionConfig, RedisConnectionMode


class StandaloneRedisClient:
    """Client for connecting to standalone Redis instances in sync or async mode."""

    def __init__(self, config: RedisConnectionConfig, async_client: bool = False):
        """
        Initialize the standalone Redis client.

        Args:
            config: Redis connection configuration
            async_client: If True, creates async Redis client. If False, creates sync client.

        Raises:
            ValueError: If configuration mode is not STANDALONE
        """
        if config.mode != RedisConnectionMode.STANDALONE:
            raise ValueError("Configuration must be for STANDALONE mode")

        self.config = config
        self.async_client = async_client

    def create_connection(self):
        """
        Create a Redis connection based on the configuration.

        Returns:
            Redis client instance (sync or async based on async_client parameter)

        Raises:
            redis.ConnectionError: If connection cannot be established
        """
        # Build connection parameters
        connection_params = {
            "host": self.config.host,
            "port": self.config.port,
            "decode_responses": True,
        }

        # Add optional parameters (include None values for testing consistency)
        connection_params["password"] = self.config.password

        if self.config.db is not None:
            connection_params["db"] = self.config.db

        if self.config.max_connections:
            connection_params["max_connections"] = self.config.max_connections

        if self.config.socket_timeout:
            connection_params["socket_timeout"] = self.config.socket_timeout

        if self.config.socket_connect_timeout:
            connection_params["socket_connect_timeout"] = (
                self.config.socket_connect_timeout
            )

        # Always set SSL parameters explicitly
        connection_params["ssl"] = self.config.ssl or False
        if self.config.ssl and self.config.ssl_cert_reqs:
            connection_params["ssl_cert_reqs"] = self.config.ssl_cert_reqs
        if self.config.ssl and self.config.ssl_ca_certs:
            connection_params["ssl_ca_certs"] = self.config.ssl_ca_certs

        # Create appropriate Redis client
        if self.async_client:
            return redis.asyncio.Redis(**connection_params)
        else:
            return redis.Redis(**connection_params)

    def __repr__(self) -> str:
        """Return string representation of the client."""
        mode = "Async" if self.async_client else "Sync"
        return f"{mode}StandaloneRedisClient({self.config.host}:{self.config.port}, mode=STANDALONE)"
