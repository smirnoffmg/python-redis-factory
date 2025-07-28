"""
Cluster Redis client implementation.

This module provides the ClusterRedisClient class for connecting to Redis Cluster deployments
in both sync and async modes.
"""

import redis
import redis.asyncio
from redis.cluster import ClusterNode

from ..interfaces import RedisConnectionConfig, RedisConnectionMode


class ClusterRedisClient:
    """Cluster Redis client for connecting to Redis Cluster deployments in sync or async mode."""

    def __init__(self, config: RedisConnectionConfig, async_client: bool = False):
        """Initialize the Cluster Redis client.

        Args:
            config: Redis connection configuration
            async_client: If True, creates async Redis client. If False, creates sync client.

        Raises:
            ValueError: If configuration is invalid for cluster mode
        """
        self._validate_config(config)
        self.config = config
        self.async_client = async_client

    def _validate_config(self, config: RedisConnectionConfig) -> None:
        """Validate the configuration for cluster mode.

        Args:
            config: Redis connection configuration

        Raises:
            ValueError: If configuration is invalid for cluster mode
        """
        if config.mode != RedisConnectionMode.CLUSTER:
            raise ValueError("Configuration must be for CLUSTER mode")

        if not config.cluster_nodes:
            raise ValueError("Cluster nodes are required for Cluster mode")

    def create_connection(self):
        """Create a Redis Cluster connection.

        Returns:
            Redis Cluster client instance (sync or async based on async_client parameter)

        Raises:
            Exception: If connection creation fails
        """
        # Parse cluster nodes into startup_nodes format
        startup_nodes = self._parse_cluster_nodes()

        # Build connection parameters
        connection_params = {
            "startup_nodes": startup_nodes,
            "decode_responses": True,
        }

        # Add optional parameters if specified
        if self.config.password:
            connection_params["password"] = self.config.password

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

        # Create appropriate Redis Cluster client
        if self.async_client:
            return redis.asyncio.RedisCluster(**connection_params)
        else:
            return redis.RedisCluster(**connection_params)

    def _parse_cluster_nodes(self):
        """Parse cluster nodes from string format to startup_nodes format.

        Returns:
            List of ClusterNode objects for startup_nodes
        """
        # We've already validated cluster_nodes is not None in _validate_config
        assert self.config.cluster_nodes is not None
        startup_nodes = []
        for node_str in self.config.cluster_nodes:
            if ":" in node_str:
                host, port_str = node_str.split(":", 1)
                port = int(port_str)
            else:
                host = node_str
                port = 6379
            startup_nodes.append(ClusterNode(host, port))
        return startup_nodes

    def __repr__(self) -> str:
        """Return string representation of the client."""
        # We've already validated cluster_nodes is not None in _validate_config
        assert self.config.cluster_nodes is not None
        nodes_str = ", ".join(self.config.cluster_nodes[:3])  # Show first 3 nodes
        if len(self.config.cluster_nodes) > 3:
            nodes_str += f", ... (+{len(self.config.cluster_nodes) - 3} more)"

        mode = "Async" if self.async_client else "Sync"
        return (
            f"{mode}ClusterRedisClient("
            f"host={self.config.host}:{self.config.port}, "
            f"mode=CLUSTER, "
            f"nodes=[{nodes_str}])"
        )
