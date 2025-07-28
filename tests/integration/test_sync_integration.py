"""
Integration tests for standalone Redis client.

This module tests the standalone Redis client with real Redis instances
using Testcontainers.
"""

import pytest
from testcontainers.redis import RedisContainer

from python_redis_factory import get_redis_client


class TestSyncStandaloneIntegration:
    """Integration tests for standalone Redis client."""

    @pytest.fixture
    def redis_container(self):
        """Create a Redis container for testing."""
        with RedisContainer("redis:7-alpine") as container:
            yield container

    def test_standalone_basic_operations(self, redis_container):
        """Test basic Redis operations with real standalone Redis."""
        # Get the connection details from the container
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        # Create Redis client using our factory
        client = get_redis_client(f"redis://{host}:{port}")

        # Test basic operations
        assert client.ping() is True

        # Test set/get operations
        client.set("test_key", "test_value")
        assert client.get("test_key") == "test_value"

        # Test delete operation
        client.delete("test_key")
        assert client.get("test_key") is None

    def test_standalone_with_database_selection(self, redis_container):
        """Test Redis operations with database selection."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        # Create clients for different databases
        client_db0 = get_redis_client(f"redis://{host}:{port}/0")
        client_db1 = get_redis_client(f"redis://{host}:{port}/1")

        # Set values in different databases
        client_db0.set("db_key", "db0_value")
        client_db1.set("db_key", "db1_value")

        # Verify values are isolated
        assert client_db0.get("db_key") == "db0_value"
        assert client_db1.get("db_key") == "db1_value"

        # Verify cross-database isolation
        client_db0.delete("db_key")
        assert client_db0.get("db_key") is None
        assert client_db1.get("db_key") == "db1_value"  # Still exists in db1

    def test_standalone_multiple_operations(self, redis_container):
        """Test multiple Redis operations in sequence."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        client = get_redis_client(f"redis://{host}:{port}")

        # Test various data types and operations
        client.set("string_key", "string_value")
        client.lpush("list_key", "item1", "item2", "item3")
        client.sadd("set_key", "member1", "member2", "member3")
        client.hset("hash_key", mapping={"field1": "value1", "field2": "value2"})

        # Verify operations
        assert client.get("string_key") == "string_value"
        assert client.lrange("list_key", 0, -1) == ["item3", "item2", "item1"]
        assert client.smembers("set_key") == {"member1", "member2", "member3"}
        assert client.hgetall("hash_key") == {"field1": "value1", "field2": "value2"}

    def test_standalone_connection_pooling(self, redis_container):
        """Test that connection pooling works correctly."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        # Create multiple clients (should reuse connections from pool)
        clients = []
        for i in range(5):
            client = get_redis_client(f"redis://{host}:{port}")
            clients.append(client)

        # Test all clients work
        for i, client in enumerate(clients):
            client.set(f"pool_test_{i}", f"value_{i}")
            assert client.get(f"pool_test_{i}") == f"value_{i}"

    def test_standalone_error_handling(self, redis_container):
        """Test error handling with real Redis."""
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

    def test_standalone_performance_basic(self, redis_container):
        """Test basic performance characteristics."""
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)

        client = get_redis_client(f"redis://{host}:{port}")

        # Test multiple operations in sequence
        for i in range(100):
            client.set(f"perf_key_{i}", f"value_{i}")
            assert client.get(f"perf_key_{i}") == f"value_{i}"
