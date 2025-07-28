#!/usr/bin/env python3
"""
Sentinel Redis Example - Synchronous

This example demonstrates how to use python-redis-factory with Redis Sentinel
in synchronous mode.
"""

from python_redis_factory import get_redis_client


def main():
    """Main function demonstrating Sentinel Redis usage."""
    print("🚀 Sentinel Redis - Synchronous Example")
    print("=" * 50)

    # Connect through Sentinel
    # Use internal hostnames when running inside Docker, external when outside
    import os

    if os.path.exists("/.dockerenv"):
        # Running inside Docker container
        sentinel_uri = "redis+sentinel://redis-sentinel-1:26379,redis-sentinel-2:26379,redis-sentinel-3:26379/mymaster"
    else:
        # Running outside Docker
        sentinel_uri = (
            "redis+sentinel://localhost:26379,localhost:26380,localhost:26381/mymaster"
        )

    client = get_redis_client(sentinel_uri)

    # Basic operations
    print("🔧 Basic Redis Operations")

    # String operations
    client.set("greeting", "Hello from Sentinel!")
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
    client.sadd("tags", "python", "redis", "sentinel", "high-availability")
    tags = client.smembers("tags")
    print(f"  Set: {tags}")

    # Sorted set operations
    client.zadd("scores", {"Alice": 100, "Bob": 85, "Charlie": 95})
    top_scores = client.zrevrange("scores", 0, 2, withscores=True)
    print(f"  Sorted Set: {top_scores}")

    # Replication info
    print("\n📊 Replication Information")
    info = client.info("replication")
    print(f"  Role: {info.get('role', 'Unknown')}")
    print(f"  Connected Slaves: {info.get('connected_slaves', 'Unknown')}")

    # Connection info
    print("\n📊 Connection Information")
    info = client.info()
    print(f"  Redis Version: {info.get('redis_version', 'Unknown')}")
    print(f"  Connected Clients: {info.get('connected_clients', 'Unknown')}")
    print(f"  Used Memory: {info.get('used_memory_human', 'Unknown')}")

    print("\n✅ Sentinel Redis example completed!")


if __name__ == "__main__":
    main()
