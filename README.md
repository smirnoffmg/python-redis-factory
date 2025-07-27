# Python Redis Factory

[![CI](https://github.com/smirnoffmg/python-redis-factory/workflows/CI/badge.svg)](https://github.com/smirnoffmg/python-redis-factory/actions)
[![Test Coverage](https://codecov.io/gh/smirnoffmg/python-redis-factory/branch/main/graph/badge.svg)](https://codecov.io/gh/smirnoffmg/python-redis-factory)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/python-redis-factory.svg)](https://pypi.org/project/python-redis-factory/)
[![Downloads](https://img.shields.io/pypi/dm/python-redis-factory.svg)](https://pypi.org/project/python-redis-factory/)

A universal Redis client factory for Python—just pass a single connection string (supporting standalone, Sentinel, or Cluster modes) and get back a ready-to-use redis.Redis instance.

## Features

- **Universal Interface**: Single API for all Redis deployment modes
- **Automatic Detection**: Automatically detects deployment mode from URI
- **Async Support**: Full async/await support with the same simple API
- **Connection Pooling**: Automatic connection pool management
- **SSL Support**: Built-in SSL/TLS support
- **Error Handling**: Comprehensive error handling and validation

## Quick Start

```python
from python_redis_factory import get_redis_client

# Standalone Redis
client = get_redis_client("redis://localhost:6379")

# Standalone with password
client = get_redis_client("redis://:secret@localhost:6379")

# Standalone with database selection
client = get_redis_client("redis://localhost:6379/1")

# Async Standalone
client = get_redis_client("redis://localhost:6379", async_client=True)

# Sentinel
client = get_redis_client("redis+sentinel://sentinel1:26379/mymaster")

# Cluster
client = get_redis_client("redis+cluster://node1:7000,node2:7001")

# SSL
client = get_redis_client("rediss://localhost:6379")
```

## Installation

```bash
pip install python-redis-factory
```

## Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd python-redis-factory

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run tests in parallel (recommended)
uv run pytest -n auto

# Run specific test categories
uv run pytest tests/unit/ -n auto      # Unit tests only
uv run pytest tests/integration/ -n auto  # Integration tests only

# Run with coverage
uv run pytest --cov=python_redis_factory -n auto

# Linting and type checking
uv run ruff check .
uv run mypy src/
```

## Testing

The project uses comprehensive testing with parallel execution:

### Test Categories
- **Unit Tests**: Fast, no external dependencies (`tests/unit/`)
- **Integration Tests**: Use testcontainers for real Redis instances (`tests/integration/`)

### Parallel Testing
Tests run in parallel by default using `pytest-xdist`:
- **Auto-detection**: `-n auto` (uses all CPU cores)
- **Fixed workers**: `-n 4` (uses 4 workers)
- **Disable parallel**: `-n 0` (sequential execution)

### Test Commands
```bash
# All tests in parallel (recommended)
uv run pytest -n auto

# Unit tests only (fast)
uv run pytest tests/unit/ -n auto

# Integration tests only (slower, requires Docker)
uv run pytest tests/integration/ -n auto

# With coverage report
uv run pytest --cov=python_redis_factory --cov-report=html -n auto

# Specific test file
uv run pytest tests/unit/test_simple_api.py -n auto
```

## Supported URI Formats

### Standalone Redis
```
redis://[user:password@]host[:port][/db]
rediss://[user:password@]host[:port][/db]  # SSL
```

### Redis Sentinel
```
redis+sentinel://[password@]sentinel1:port,sentinel2:port/service_name
```

### Redis Cluster
```
redis+cluster://[password@]node1:port,node2:port
```

## API Reference

### `get_redis_client(redis_dsn: str, async_client: bool = False)`

Creates a Redis client from a connection string.

**Parameters:**
- `redis_dsn`: Redis connection string (URI format)
- `async_client`: If True, returns an async Redis client

**Returns:**
- A Redis client instance (sync or async)

**Examples:**
```python
# Sync client
client = get_redis_client("redis://localhost:6379")
result = client.get("key")

# Async client
client = get_redis_client("redis://localhost:6379", async_client=True)
result = await client.get("key")
```

