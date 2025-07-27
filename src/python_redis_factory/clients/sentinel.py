"""
Sentinel Redis client implementation.

This module provides the SentinelRedisClient class for connecting to
Redis Sentinel deployments in both sync and async modes.
"""

from typing import List, Tuple

import redis
import redis.asyncio

from ..interfaces import RedisConnectionConfig, RedisConnectionMode


class SentinelRedisClient:
    """Client for connecting to Redis Sentinel deployments in sync or async mode."""

    def __init__(self, config: RedisConnectionConfig, async_client: bool = False):
        """
        Initialize the Sentinel Redis client.

        Args:
            config: Redis connection configuration
            async_client: If True, creates async Redis client. If False, creates sync client.

        Raises:
            ValueError: If configuration mode is not SENTINEL or missing required fields
        """
        if config.mode != RedisConnectionMode.SENTINEL:
            raise ValueError("Configuration must be for SENTINEL mode")

        if not config.sentinel_hosts:
            raise ValueError("Sentinel hosts are required for Sentinel mode")

        if not config.service_name:
            raise ValueError("Service name is required for Sentinel mode")

        self.config = config
        self.async_client = async_client

    def _parse_sentinel_hosts(self) -> List[Tuple[str, int]]:
        """
        Parse sentinel hosts from string format to tuple format.

        Returns:
            List of (host, port) tuples for sentinel hosts
        """
        # We've already validated sentinel_hosts is not None in __init__
        assert self.config.sentinel_hosts is not None
        parsed_hosts = []
        for host_str in self.config.sentinel_hosts:
            if ":" in host_str:
                host, port_str = host_str.split(":", 1)
                port = int(port_str)
            else:
                host = host_str
                port = 26379  # Default sentinel port
            parsed_hosts.append((host, port))
        return parsed_hosts

    def create_connection(self):
        """
        Create a Redis connection through Sentinel.

        Returns:
            Redis client instance (connected to master, sync or async based on async_client parameter)

        Raises:
            redis.ConnectionError: If connection cannot be established
        """
        # Parse sentinel hosts
        sentinel_hosts = self._parse_sentinel_hosts()

        # Build connection parameters
        connection_params = {
            "password": self.config.password,
            "max_connections": self.config.max_connections,
            "socket_timeout": self.config.socket_timeout,
            "socket_connect_timeout": self.config.socket_connect_timeout,
            "decode_responses": True,  # Always decode responses to strings
        }

        # Add SSL parameters
        connection_params["ssl"] = self.config.ssl
        if self.config.ssl and self.config.ssl_cert_reqs:
            connection_params["ssl_cert_reqs"] = self.config.ssl_cert_reqs
        if self.config.ssl and self.config.ssl_ca_certs:
            connection_params["ssl_ca_certs"] = self.config.ssl_ca_certs

        # Create appropriate Sentinel instance
        if self.async_client:
            sentinel = redis.asyncio.sentinel.Sentinel(
                sentinel_hosts, **connection_params
            )
        else:
            sentinel = redis.sentinel.Sentinel(sentinel_hosts, **connection_params)

        # Get master client
        assert self.config.service_name is not None
        master_client = sentinel.master_for(self.config.service_name)

        return master_client

    def __repr__(self) -> str:
        """Return string representation of the client."""
        # We've already validated sentinel_hosts is not None in __init__
        assert self.config.sentinel_hosts is not None
        hosts_str = ", ".join(self.config.sentinel_hosts)
        mode = "Async" if self.async_client else "Sync"
        return f"{mode}SentinelRedisClient({hosts_str}, service={self.config.service_name})"
