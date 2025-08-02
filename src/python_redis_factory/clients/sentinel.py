"""
Sentinel Redis client implementation.

This module provides the SentinelRedisClient class for connecting to
Redis Sentinel deployments in both sync and async modes.
"""

from typing import List, Tuple

import redis
import redis.asyncio

from ..interfaces import RedisClient, RedisConnectionConfig, RedisConnectionMode


class SentinelRedisClient:
    """A builder for creating Redis Sentinel clients."""

    @staticmethod
    async def create(
        config: RedisConnectionConfig, async_client: bool = False
    ) -> RedisClient:
        """
        Create a Redis connection through Sentinel.

        Args:
            config: Redis connection configuration.
            async_client: If True, creates an async Redis client.

        Returns:
            A Redis client instance connected to the master.

        Raises:
            ValueError: If the configuration is invalid for Sentinel mode.
            redis.ConnectionError: If the connection cannot be established.
        """
        if config.mode != RedisConnectionMode.SENTINEL:
            raise ValueError("Configuration must be for SENTINEL mode")
        if not config.sentinel_hosts:
            raise ValueError("Sentinel hosts are required for Sentinel mode")
        if not config.service_name:
            raise ValueError("Service name is required for Sentinel mode")

        sentinel_hosts = SentinelRedisClient._parse_sentinel_hosts(config)

        connection_params = {
            "password": config.password,
            "max_connections": config.max_connections,
            "socket_timeout": config.socket_timeout,
            "socket_connect_timeout": config.socket_connect_timeout,
            "decode_responses": True,
        }

        if config.ssl:
            connection_params["ssl"] = True
            if config.ssl_cert_reqs:
                connection_params["ssl_cert_reqs"] = config.ssl_cert_reqs
            if config.ssl_ca_certs:
                connection_params["ssl_ca_certs"] = config.ssl_ca_certs

        if async_client:
            sentinel = redis.asyncio.sentinel.Sentinel(
                sentinel_hosts, **connection_params
            )
        else:
            sentinel = redis.sentinel.Sentinel(sentinel_hosts, **connection_params)

        return sentinel.master_for(config.service_name)

    @staticmethod
    def _parse_sentinel_hosts(config: RedisConnectionConfig) -> List[Tuple[str, int]]:
        """Parse sentinel hosts from string format to tuple format."""
        assert config.sentinel_hosts is not None
        parsed_hosts = []
        for host_str in config.sentinel_hosts:
            if ":" in host_str:
                host, port_str = host_str.split(":", 1)
                port = int(port_str)
            else:
                host = host_str
                port = 26379  # Default sentinel port
            parsed_hosts.append((host, port))
        return parsed_hosts
