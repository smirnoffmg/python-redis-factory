"""
Core interfaces for the Python Redis Factory.

This module defines the fundamental interfaces and types used throughout
the redis factory implementation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RedisConnectionMode(Enum):
    """Enumeration of supported Redis connection modes."""

    STANDALONE = "standalone"
    SENTINEL = "sentinel"
    CLUSTER = "cluster"


@dataclass
class RedisConnectionConfig:
    """Configuration for Redis connection parameters."""

    host: str
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    mode: RedisConnectionMode = RedisConnectionMode.STANDALONE

    # Sentinel-specific configuration
    sentinel_hosts: Optional[list[str]] = None
    sentinel_password: Optional[str] = None
    service_name: Optional[str] = None

    # Cluster-specific configuration
    cluster_nodes: Optional[list[str]] = None

    # Connection pool configuration
    max_connections: int = 10
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0

    # SSL configuration
    ssl: bool = False
    ssl_cert_reqs: Optional[str] = None
    ssl_ca_certs: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.port < 1 or self.port > 65535:
            raise ValueError("Port must be between 1 and 65535")

        if self.db < 0:
            raise ValueError("Database number must be non-negative")

        if self.max_connections < 1:
            raise ValueError("Max connections must be at least 1")

        if self.socket_timeout < 0:
            raise ValueError("Socket timeout must be non-negative")

        if self.socket_connect_timeout < 0:
            raise ValueError("Socket connect timeout must be non-negative")
