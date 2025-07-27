"""
Redis URI parser module.

This module provides functionality to parse Redis URIs and convert them
into RedisConnectionConfig objects.
"""

from typing import List
from urllib.parse import ParseResult, urlparse

from .interfaces import RedisConnectionConfig, RedisConnectionMode


def parse_redis_uri(uri: str) -> RedisConnectionConfig:
    """
    Parse a Redis URI and return a RedisConnectionConfig object.

    Supported URI formats:
    - Standalone: redis://[user:password@]host[:port][/db]
    - Sentinel: redis+sentinel://[password@]sentinel1:port,sentinel2:port/service_name
    - Cluster: redis+cluster://[password@]node1:port,node2:port
    - SSL: rediss://[user:password@]host[:port][/db]

    Args:
        uri: Redis connection URI

    Returns:
        RedisConnectionConfig object with parsed parameters

    Raises:
        ValueError: If URI format is invalid or unsupported
    """
    if not uri:
        raise ValueError("URI cannot be empty")

    # Parse the URI
    try:
        parsed = urlparse(uri)
    except Exception:
        raise ValueError("Invalid Redis URI format")

    # Validate basic URI structure
    if not parsed.scheme:
        raise ValueError("Invalid Redis URI format")

    # Determine connection mode and validate scheme
    mode = _determine_connection_mode(parsed.scheme)

    if mode == RedisConnectionMode.STANDALONE:
        if not parsed.netloc:
            raise ValueError("Invalid Redis URI format")
        return _parse_standalone_uri(parsed)
    elif mode == RedisConnectionMode.SENTINEL:
        return _parse_sentinel_uri(parsed)
    elif mode == RedisConnectionMode.CLUSTER:
        return _parse_cluster_uri(parsed)
    else:
        raise ValueError(f"Unsupported connection mode: {mode}")


def _determine_connection_mode(scheme: str) -> RedisConnectionMode:
    """Determine the connection mode from the URI scheme."""
    if scheme in ("redis", "rediss"):
        return RedisConnectionMode.STANDALONE
    elif scheme == "redis+sentinel":
        return RedisConnectionMode.SENTINEL
    elif scheme == "redis+cluster":
        return RedisConnectionMode.CLUSTER
    else:
        raise ValueError(f"Invalid Redis URI scheme: {scheme}")


def _parse_standalone_uri(parsed: ParseResult) -> RedisConnectionConfig:
    """Parse a standalone Redis URI."""
    # Extract host and port
    host = parsed.hostname or "localhost"

    # Handle port validation
    try:
        port = parsed.port or 6379
    except ValueError:
        raise ValueError("Invalid port number")

    # Extract authentication
    password = None
    if parsed.password:
        password = parsed.password

    # Extract database number
    db = 0
    if parsed.path and len(parsed.path) > 1:
        try:
            db = int(parsed.path[1:])  # Remove leading '/'
            if db < 0:
                raise ValueError("Invalid database number")
        except ValueError:
            raise ValueError("Invalid database number")

    # Determine if SSL is enabled
    ssl = parsed.scheme == "rediss"

    return RedisConnectionConfig(
        host=host,
        port=port,
        password=password,
        db=db,
        mode=RedisConnectionMode.STANDALONE,
        ssl=ssl,
    )


def _parse_sentinel_uri(parsed: ParseResult) -> RedisConnectionConfig:
    """Parse a Sentinel Redis URI."""
    # Extract sentinel hosts from netloc
    sentinel_hosts = _parse_host_list(parsed.netloc)
    if not sentinel_hosts:
        raise ValueError("Sentinel URI must include at least one sentinel host")

    # Extract service name from path
    if not parsed.path or len(parsed.path) <= 1:
        raise ValueError("Sentinel URI must include service name")

    service_name = parsed.path[1:]  # Remove leading '/'

    # Extract password if present
    password = None
    if parsed.password:
        password = parsed.password

    # Use first sentinel as default host/port
    first_sentinel = sentinel_hosts[0]
    host, port = _parse_host_port(first_sentinel)

    return RedisConnectionConfig(
        host=host,
        port=port,
        password=password,
        mode=RedisConnectionMode.SENTINEL,
        sentinel_hosts=sentinel_hosts,
        sentinel_password=password,
        service_name=service_name,
    )


def _parse_cluster_uri(parsed: ParseResult) -> RedisConnectionConfig:
    """Parse a Cluster Redis URI."""
    # Extract cluster nodes from netloc
    cluster_nodes = _parse_host_list(parsed.netloc)
    if not cluster_nodes:
        raise ValueError("Cluster URI must include at least one node")

    # Extract password if present
    password = None
    if parsed.password:
        password = parsed.password

    # Use first node as default host/port
    first_node = cluster_nodes[0]
    host, port = _parse_host_port(first_node)

    return RedisConnectionConfig(
        host=host,
        port=port,
        password=password,
        mode=RedisConnectionMode.CLUSTER,
        cluster_nodes=cluster_nodes,
    )


def _parse_host_list(netloc: str) -> List[str]:
    """Parse a comma-separated list of hosts from netloc."""
    if not netloc:
        return []

    # Remove authentication part if present
    if "@" in netloc:
        netloc = netloc.split("@", 1)[1]

    return [host.strip() for host in netloc.split(",") if host.strip()]


def _parse_host_port(host_port: str) -> tuple[str, int]:
    """Parse host:port string into host and port tuple."""
    if ":" in host_port:
        host, port_str = host_port.rsplit(":", 1)
        try:
            port = int(port_str)
            if port < 1 or port > 65535:
                raise ValueError("Port must be between 1 and 65535")
        except ValueError:
            raise ValueError("Invalid port number")
    else:
        host = host_port
        port = 6379

    return host, port
