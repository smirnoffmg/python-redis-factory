"""
End-to-End integration tests for Redis client factory.

This module tests the complete workflow with different URIs, error scenarios,
and performance characteristics using real Redis instances.
"""

import time

import pytest
from testcontainers.redis import RedisContainer

from python_redis_factory import get_redis_client


class TestE2EIntegration:
    """End-to-End integration tests for Redis client factory."""

    @pytest.fixture
    def redis_container(self):
        """Create a Redis container for testing."""
        with RedisContainer("redis:7-alpine") as container:
            yield container

    def test_e2e_standalone_workflow(self, redis_container):
        """Test complete standalone Redis workflow."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        # Test different URI formats
        uris = [
            f"redis://{host}:{port}",
            f"redis://{host}:{port}/0",
            f"redis://{host}:{port}/1",
        ]

        for uri in uris:
            client = get_redis_client(uri)

            # Test basic operations
            assert client.ping() is True

            # Test data operations
            client.set("e2e_key", "e2e_value")
            assert client.get("e2e_key") == "e2e_value"

            # Clean up
            client.delete("e2e_key")

    @pytest.mark.asyncio
    async def test_e2e_async_standalone_workflow(self, redis_container):
        """Test complete async standalone Redis workflow."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        # Test different URI formats
        uris = [
            f"redis://{host}:{port}",
            f"redis://{host}:{port}/0",
            f"redis://{host}:{port}/1",
        ]

        for uri in uris:
            client = get_redis_client(uri, async_client=True)

            # Test basic operations
            assert await client.ping() is True

            # Test data operations
            await client.set("e2e_async_key", "e2e_async_value")
            result = await client.get("e2e_async_key")
            assert result == "e2e_async_value"

            # Clean up
            await client.delete("e2e_async_key")

    def test_e2e_error_scenarios(self, redis_container):
        """Test error scenarios with real Redis."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        client = get_redis_client(f"redis://{host}:{port}")

        # Test invalid operations
        client.set("string_key", "string_value")  # Set up a string key first
        with pytest.raises(
            Exception
        ):  # Redis will raise an error for invalid operations
            client.lpush("string_key", "item")  # Try to use list operation on string

        # Test operations on non-existent keys
        assert client.get("non_existent_key") is None
        assert client.exists("non_existent_key") == 0

    @pytest.mark.asyncio
    async def test_e2e_async_error_scenarios(self, redis_container):
        """Test async error scenarios with real Redis."""
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

    def test_e2e_performance_characteristics(self, redis_container):
        """Test performance characteristics with real Redis."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        client = get_redis_client(f"redis://{host}:{port}")

        # Test bulk operations performance
        start_time = time.time()

        # Set 1000 keys
        for i in range(1000):
            client.set(f"perf_key_{i}", f"value_{i}")

        set_time = time.time() - start_time

        # Get 1000 keys
        start_time = time.time()
        for i in range(1000):
            result = client.get(f"perf_key_{i}")
            assert result == f"value_{i}"

        get_time = time.time() - start_time

        # Clean up
        for i in range(1000):
            client.delete(f"perf_key_{i}")

        # Performance should be reasonable (less than 10 seconds for 1000 operations)
        assert set_time < 10.0, f"Set operations took {set_time:.2f} seconds"
        assert get_time < 10.0, f"Get operations took {get_time:.2f} seconds"

    @pytest.mark.asyncio
    async def test_e2e_async_performance_characteristics(self, redis_container):
        """Test async performance characteristics with real Redis."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        client = get_redis_client(f"redis://{host}:{port}", async_client=True)

        # Test bulk operations performance
        start_time = time.time()

        # Set 1000 keys
        for i in range(1000):
            await client.set(f"perf_async_key_{i}", f"value_{i}")

        set_time = time.time() - start_time

        # Get 1000 keys
        start_time = time.time()
        for i in range(1000):
            result = await client.get(f"perf_async_key_{i}")
            assert result == f"value_{i}"

        get_time = time.time() - start_time

        # Clean up
        for i in range(1000):
            await client.delete(f"perf_async_key_{i}")

        # Performance should be reasonable (less than 10 seconds for 1000 operations)
        assert set_time < 10.0, f"Async set operations took {set_time:.2f} seconds"
        assert get_time < 10.0, f"Async get operations took {get_time:.2f} seconds"

    def test_e2e_connection_pooling(self, redis_container):
        """Test connection pooling characteristics."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        # Create multiple clients (should reuse connections from pool)
        clients = []
        for i in range(10):
            client = get_redis_client(f"redis://{host}:{port}")
            clients.append(client)

        # Test all clients work simultaneously
        for i, client in enumerate(clients):
            client.set(f"pool_e2e_key_{i}", f"pool_value_{i}")
            result = client.get(f"pool_e2e_key_{i}")
            assert result == f"pool_value_{i}"

        # Clean up
        for i, client in enumerate(clients):
            client.delete(f"pool_e2e_key_{i}")

    @pytest.mark.asyncio
    async def test_e2e_async_connection_pooling(self, redis_container):
        """Test async connection pooling characteristics."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        # Create multiple async clients (should reuse connections from pool)
        clients = []
        for i in range(10):
            client = get_redis_client(f"redis://{host}:{port}", async_client=True)
            clients.append(client)

        # Test all clients work simultaneously
        for i, client in enumerate(clients):
            await client.set(f"pool_async_e2e_key_{i}", f"pool_async_value_{i}")
            result = await client.get(f"pool_async_e2e_key_{i}")
            assert result == f"pool_async_value_{i}"

        # Clean up
        for i, client in enumerate(clients):
            await client.delete(f"pool_async_e2e_key_{i}")

    def test_e2e_data_types_and_operations(self, redis_container):
        """Test all Redis data types and operations."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        client = get_redis_client(f"redis://{host}:{port}")

        # Test Strings
        client.set("string_key", "string_value")
        assert client.get("string_key") == "string_value"

        # Test Lists
        client.lpush("list_key", "item1", "item2", "item3")
        assert client.lrange("list_key", 0, -1) == ["item3", "item2", "item1"]

        # Test Sets
        client.sadd("set_key", "member1", "member2", "member3")
        assert client.smembers("set_key") == {"member1", "member2", "member3"}

        # Test Hashes
        client.hset("hash_key", mapping={"field1": "value1", "field2": "value2"})
        assert client.hgetall("hash_key") == {"field1": "value1", "field2": "value2"}

        # Test Sorted Sets
        client.zadd("zset_key", {"member1": 1.0, "member2": 2.0, "member3": 3.0})
        assert client.zrange("zset_key", 0, -1) == ["member1", "member2", "member3"]

        # Clean up
        client.delete("string_key", "list_key", "set_key", "hash_key", "zset_key")

    @pytest.mark.asyncio
    async def test_e2e_async_data_types_and_operations(self, redis_container):
        """Test all Redis data types and operations with async client."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        client = get_redis_client(f"redis://{host}:{port}", async_client=True)

        # Test Strings
        await client.set("async_string_key", "async_string_value")
        result = await client.get("async_string_key")
        assert result == "async_string_value"

        # Test Lists
        await client.lpush("async_list_key", "item1", "item2", "item3")
        result = await client.lrange("async_list_key", 0, -1)
        assert result == ["item3", "item2", "item1"]

        # Test Sets
        await client.sadd("async_set_key", "member1", "member2", "member3")
        result = await client.smembers("async_set_key")
        assert result == {"member1", "member2", "member3"}

        # Test Hashes
        await client.hset(
            "async_hash_key", mapping={"field1": "value1", "field2": "value2"}
        )
        result = await client.hgetall("async_hash_key")
        assert result == {"field1": "value1", "field2": "value2"}

        # Test Sorted Sets
        await client.zadd(
            "async_zset_key", {"member1": 1.0, "member2": 2.0, "member3": 3.0}
        )
        result = await client.zrange("async_zset_key", 0, -1)
        assert result == ["member1", "member2", "member3"]

        # Clean up
        await client.delete(
            "async_string_key",
            "async_list_key",
            "async_set_key",
            "async_hash_key",
            "async_zset_key",
        )

    def test_e2e_uri_parsing_edge_cases(self, redis_container):
        """Test URI parsing edge cases with real Redis."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        # Test various URI formats
        uris = [
            f"redis://{host}:{port}",
            f"redis://{host}:{port}/",
            f"redis://{host}:{port}/0",
            f"redis://{host}:{port}/1",
            f"redis://{host}:{port}/15",
        ]

        for uri in uris:
            client = get_redis_client(uri)
            assert client.ping() is True

    def test_e2e_concurrent_access(self, redis_container):
        """Test concurrent access to Redis."""
        import queue
        import threading

        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        results = queue.Queue()
        errors = queue.Queue()

        def worker(worker_id):
            try:
                client = get_redis_client(f"redis://{host}:{port}")

                # Perform operations
                for i in range(100):
                    key = f"concurrent_key_{worker_id}_{i}"
                    value = f"value_{worker_id}_{i}"

                    client.set(key, value)
                    result = client.get(key)

                    if result == value:
                        results.put(True)
                    else:
                        results.put(False)

            except Exception as e:
                errors.put(e)

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        assert errors.empty(), (
            f"Errors occurred: {[errors.get() for _ in range(errors.qsize())]}"
        )

        # All operations should have succeeded
        success_count = 0
        while not results.empty():
            if results.get():
                success_count += 1

        assert success_count == 500, (
            f"Expected 500 successful operations, got {success_count}"
        )
