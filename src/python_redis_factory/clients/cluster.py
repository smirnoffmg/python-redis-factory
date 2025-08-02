"""
Cluster Redis client implementation.

This module provides the ClusterRedisClient class for connecting to Redis Cluster deployments
in both sync and async modes.
"""

from redis.asyncio.cluster import RedisCluster as AsyncRedisCluster
from redis.cluster import ClusterNode, RedisCluster

from ..interfaces import RedisClient, RedisConnectionConfig, RedisConnectionMode


class ClusterRedisClient:
    """A builder for creating Redis Cluster clients."""

    @staticmethod
    async def create(
        config: RedisConnectionConfig, async_client: bool = False
    ) -> RedisClient:
        """
        Create a Redis Cluster connection.

        Args:
            config: Redis connection configuration.
            async_client: If True, creates an async Redis client.

        Returns:
            A Redis Cluster client instance.

        Raises:
            ValueError: If the configuration is invalid for cluster mode.
            Exception: If connection creation fails.
        """
        ClusterRedisClient._validate_config(config)
        startup_nodes = ClusterRedisClient._parse_cluster_nodes(config)

        connection_params = {
            "startup_nodes": startup_nodes,
            "decode_responses": True,
        }

        if config.password:
            connection_params["password"] = config.password
        if config.max_connections:
            connection_params["max_connections"] = config.max_connections
        if config.socket_timeout:
            connection_params["socket_timeout"] = config.socket_timeout
        if config.socket_connect_timeout:
            connection_params["socket_connect_timeout"] = config.socket_connect_timeout

        if config.ssl:
            connection_params["ssl"] = True
            if config.ssl_cert_reqs:
                connection_params["ssl_cert_reqs"] = config.ssl_cert_reqs

        if async_client:
            return AsyncRedisCluster(**connection_params)
        else:
            return RedisCluster(**connection_params)

    @staticmethod
    def _validate_config(config: RedisConnectionConfig) -> None:
        """Validate the configuration for cluster mode."""
        if config.mode != RedisConnectionMode.CLUSTER:
            raise ValueError("Configuration must be for CLUSTER mode")
        if not config.cluster_nodes:
            raise ValueError("Cluster nodes are required for Cluster mode")

    @staticmethod
    def _parse_cluster_nodes(config: RedisConnectionConfig):
        """Parse cluster nodes from string format to startup_nodes format."""
        assert config.cluster_nodes is not None
        startup_nodes = []
        for node_str in config.cluster_nodes:
            if ":" in node_str:
                host, port_str = node_str.split(":", 1)
                port = int(port_str)
            else:
                host = node_str
                port = 6379
            startup_nodes.append(ClusterNode(host, port))
        return startup_nodes
