#!/usr/bin/env python3
"""
Standalone Redis Example - Synchronous

This example demonstrates how to use python-redis-factory with standalone Redis
in synchronous mode.
"""

from python_redis_factory import get_redis_client


def main():
    """Main function demonstrating standalone Redis usage."""
    print("🚀 Standalone Redis - Synchronous Example")
    print("=" * 50)

    # Connect to Redis
    client = get_redis_client("redis://:redis123@localhost:6379")

    # Basic operations
    print("🔧 Basic Redis Operations")

    # String operations
    client.set("greeting", "Hello from python-redis-factory!")
    greeting = client.get("greeting")
    print(f"  Set/Get: {greeting}")

    # List operations
    client.lpush("items", "item1", "item2", "item3")
    items = client.lrange("items", 0, -1)
    print(f"  List: {items}")

    # Hash operations
    client.hset("user:1", mapping={"name": "Alice", "age": "30", "city": "New York"})
    user = client.hgetall("user:1")
    print(f"  Hash: {user}")

    # Set operations
    client.sadd("tags", "python", "redis", "sync", "fast")
    tags = client.smembers("tags")
    print(f"  Set: {tags}")

    # Sorted set operations
    client.zadd("scores", {"Alice": 100, "Bob": 85, "Charlie": 95})
    top_scores = client.zrevrange("scores", 0, 2, withscores=True)
    print(f"  Sorted Set: {top_scores}")

    # Connection info
    print("\n📊 Connection Information")
    info = client.info()
    print(f"  Redis Version: {info.get('redis_version', 'Unknown')}")
    print(f"  Connected Clients: {info.get('connected_clients', 'Unknown')}")
    print(f"  Used Memory: {info.get('used_memory_human', 'Unknown')}")

    print("\n✅ Standalone Redis example completed!")


if __name__ == "__main__":
    main()
