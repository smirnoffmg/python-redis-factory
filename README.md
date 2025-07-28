# Python Redis Factory

[![CI](https://github.com/smirnoffmg/python-redis-factory/workflows/CI/badge.svg)](https://github.com/smirnoffmg/python-redis-factory/actions)
[![Test Coverage](https://codecov.io/gh/smirnoffmg/python-redis-factory/branch/main/graph/badge.svg)](https://codecov.io/gh/smirnoffmg/python-redis-factory)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/python-redis-factory.svg)](https://pypi.org/project/python-redis-factory/)
[![Downloads](https://img.shields.io/pypi/dm/python-redis-factory.svg)](https://pypi.org/project/python-redis-factory/)

A universal Redis client factory for Python — just pass a single connection string and get back a ready-to-use `redis.Redis` instance (both sync and async).

## Features

- **Universal Interface**: Single API for standalone, Sentinel, and Cluster modes
- **Automatic Detection**: Detects deployment mode from URI
- **Async Support**: Full async/await support
- **Connection Pooling**: Automatic pool management
- **SSL Support**: Built-in SSL/TLS support

## Quick Start

```python
from python_redis_factory import get_redis_client
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

# Standalone Redis (sync)
client: Redis = get_redis_client("redis://localhost:6379")

# Standalone Redis (async)
async_client: AsyncRedis = get_redis_client("redis://localhost:6379", async_client=True)

# Sentinel (sync)
sentinel_client: Redis = get_redis_client("redis+sentinel://sentinel1:26379/mymaster")

# Sentinel (async)
async_sentinel_client: AsyncRedis = get_redis_client("redis+sentinel://sentinel1:26379/mymaster", async_client=True)

# Cluster (sync)
cluster_client: Redis = get_redis_client("redis+cluster://node1:7000,node2:7001")

# Cluster (async)
async_cluster_client: AsyncRedis = get_redis_client("redis+cluster://node1:7000,node2:7001", async_client=True)

# SSL (sync)
ssl_client: Redis = get_redis_client("rediss://localhost:6379")

# SSL (async)
async_ssl_client: AsyncRedis = get_redis_client("rediss://localhost:6379", async_client=True)
```

## Installation

```bash
pip install python-redis-factory
```

## Development

```bash
# Install dependencies
make install

# Run tests
make test-parallel

# Run quality checks
make ci

# Show all commands
make help
```

## Documentation

- [Examples](examples/) - Comprehensive examples with Docker Compose
- [Release Guide](docs/RELEASE.md) - How to make releases
- [Release Checklist](docs/RELEASE_CHECKLIST.md) - Pre-release checklist

## Supported URI Formats

```
# Standalone
redis://[user:password@]host[:port][/db]
rediss://[user:password@]host[:port][/db]  # SSL

# Sentinel
redis+sentinel://[password@]sentinel1:port,sentinel2:port/service_name

# Cluster
redis+cluster://[password@]node1:port,node2:port
```

