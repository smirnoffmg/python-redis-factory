"""
Redis client factory.

This module provides a factory for creating Redis clients.
"""

from typing import Awaitable, Callable, Dict, Union

from .interfaces import (
    RedisClient,
    RedisConnectionConfig,
    RedisConnectionMode,
)

RedisClientBuilder = Union[
    Callable[[RedisConnectionConfig, bool], RedisClient],
    Callable[[RedisConnectionConfig, bool], Awaitable[RedisClient]],
]


class RedisClientFactory:
    """A factory for creating Redis clients."""

    def __init__(self) -> None:
        self._builders: Dict[RedisConnectionMode, RedisClientBuilder] = {}

    def register_builder(
        self, mode: RedisConnectionMode, builder: RedisClientBuilder
    ) -> None:
        """
        Register a builder for a given connection mode.

        Args:
            mode: The connection mode to register the builder for.
            builder: The builder to register.
        """
        self._builders[mode] = builder

    async def create_client(
        self, config: RedisConnectionConfig, async_client: bool = False
    ) -> RedisClient:
        """
        Create a Redis client for the given configuration.

        Args:
            config: The Redis connection configuration.
            async_client: Whether to create an async client.

        Returns:
            A Redis client instance.

        Raises:
            NotImplementedError: If no builder is registered for the given mode.
        """
        builder = self._builders.get(config.mode)
        if not builder:
            raise NotImplementedError(
                f"Client creation for {config.mode} mode not yet implemented"
            )
        if async_client:
            return await builder(config, async_client)
        else:
            return builder(config, async_client)
