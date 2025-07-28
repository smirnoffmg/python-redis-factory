"""
Async integration tests for Redis client factory.

This module tests the async Redis client functionality with real Redis instances
using Testcontainers.
"""

import pytest
from testcontainers.redis import RedisContainer

from python_redis_factory import get_redis_client


class TestAsyncStandaloneIntegration:
    """Async integration tests for Redis client factory."""

    @pytest.fixture
    def redis_container(self):
        """Create a Redis container for testing."""
        with RedisContainer("redis:7-alpine") as container:
            yield container

    @pytest.mark.asyncio
    async def test_async_standalone_basic_operations(self, redis_container):
        """Test basic async Redis operations with real standalone Redis."""
        # Get the connection details from the container
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        # Create async Redis client using our factory
        client = get_redis_client(f"redis://{host}:{port}", async_client=True)

        # Test basic operations
        assert await client.ping() is True

        # Test set/get operations
        await client.set("test_key", "test_value")
        result = await client.get("test_key")
        assert result == "test_value"

        # Test delete operation
        await client.delete("test_key")
        result = await client.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_async_standalone_with_database_selection(self, redis_container):
        """Test async Redis operations with database selection."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        # Create async clients for different databases
        client_db0 = get_redis_client(f"redis://{host}:{port}/0", async_client=True)
        client_db1 = get_redis_client(f"redis://{host}:{port}/1", async_client=True)

        # Set values in different databases
        await client_db0.set("db_key", "db0_value")
        await client_db1.set("db_key", "db1_value")

        # Verify values are isolated
        result_db0 = await client_db0.get("db_key")
        result_db1 = await client_db1.get("db_key")
        assert result_db0 == "db0_value"
        assert result_db1 == "db1_value"

        # Verify cross-database isolation
        await client_db0.delete("db_key")
        result_db0 = await client_db0.get("db_key")
        result_db1 = await client_db1.get("db_key")
        assert result_db0 is None
        assert result_db1 == "db1_value"  # Still exists in db1

    @pytest.mark.asyncio
    async def test_async_standalone_multiple_operations(self, redis_container):
        """Test multiple async Redis operations in sequence."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        client = get_redis_client(f"redis://{host}:{port}", async_client=True)

        # Test various data types and operations
        await client.set("string_key", "string_value")
        await client.lpush("list_key", "item1", "item2", "item3")
        await client.sadd("set_key", "member1", "member2", "member3")
        await client.hset("hash_key", mapping={"field1": "value1", "field2": "value2"})

        # Verify operations
        string_result = await client.get("string_key")
        list_result = await client.lrange("list_key", 0, -1)
        set_result = await client.smembers("set_key")
        hash_result = await client.hgetall("hash_key")

        assert string_result == "string_value"
        assert list_result == ["item3", "item2", "item1"]
        assert set_result == {"member1", "member2", "member3"}
        assert hash_result == {"field1": "value1", "field2": "value2"}

    @pytest.mark.asyncio
    async def test_async_standalone_connection_pooling(self, redis_container):
        """Test that async connection pooling works correctly."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        # Create multiple async clients (should reuse connections from pool)
        clients = []
        for i in range(5):
            client = get_redis_client(f"redis://{host}:{port}", async_client=True)
            clients.append(client)

        # Test all clients work
        for i, client in enumerate(clients):
            await client.set(f"pool_test_{i}", f"value_{i}")
            result = await client.get(f"pool_test_{i}")
            assert result == f"value_{i}"

    @pytest.mark.asyncio
    async def test_async_standalone_error_handling(self, redis_container):
        """Test async error handling with real Redis."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        client = get_redis_client(f"redis://{host}:{port}", async_client=True)

        # Test invalid operations
        await client.set("string_key", "string_value")  # Set up a string key first
        with pytest.raises(
            Exception
        ):  # Redis will raise an error for invalid operations
            await client.lpush(
                "string_key", "item"
            )  # Try to use list operation on string

        # Test operations on non-existent keys
        result = await client.get("non_existent_key")
        assert result is None
        exists = await client.exists("non_existent_key")
        assert exists == 0

    @pytest.mark.asyncio
    async def test_async_standalone_performance_basic(self, redis_container):
        """Test basic async performance characteristics."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        client = get_redis_client(f"redis://{host}:{port}", async_client=True)

        # Test multiple operations in sequence
        for i in range(100):
            await client.set(f"perf_key_{i}", f"value_{i}")
            result = await client.get(f"perf_key_{i}")
            assert result == f"value_{i}"

    @pytest.mark.asyncio
    async def test_async_standalone_concurrent_operations(self, redis_container):
        """Test concurrent async operations."""
        import asyncio

        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        client = get_redis_client(f"redis://{host}:{port}", async_client=True)

        # Create multiple concurrent tasks
        tasks = []
        for i in range(10):
            task = client.set(f"concurrent_key_{i}", f"value_{i}")
            tasks.append(task)

        # Execute all tasks concurrently
        await asyncio.gather(*tasks)

        # Verify all values were set
        for i in range(10):
            result = await client.get(f"concurrent_key_{i}")
            assert result == f"value_{i}"
