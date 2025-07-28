#!/usr/bin/env python3
"""
Cluster Redis Example - Synchronous

This example demonstrates how to use python-redis-factory with Redis Cluster
in synchronous mode.
"""

from python_redis_factory import get_redis_client


def main():
    """Main function demonstrating Cluster Redis usage."""
    print("🚀 Cluster Redis - Synchronous Example")
    print("=" * 50)

    # Connect to Redis Cluster
    client = get_redis_client(
        "redis+cluster://:redis123@localhost:7001,localhost:7002,localhost:7003,localhost:7004,localhost:7005,localhost:7006"
    )

    # Basic operations
    print("🔧 Basic Redis Operations")

    # String operations
    client.set("greeting", "Hello from Cluster!")
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
    client.sadd("tags", "python", "redis", "cluster", "distributed")
    tags = client.smembers("tags")
    print(f"  Set: {tags}")

    # Sorted set operations
    client.zadd("scores", {"Alice": 100, "Bob": 85, "Charlie": 95})
    top_scores = client.zrevrange("scores", 0, 2, withscores=True)
    print(f"  Sorted Set: {top_scores}")

    # Cluster info
    print("\n📊 Cluster Information")
    try:
        cluster_info = client.cluster_info()
        print(f"  Cluster State: {cluster_info.get('cluster_state', 'Unknown')}")
        print(
            f"  Slots Assigned: {cluster_info.get('cluster_slots_assigned', 'Unknown')}"
        )
        print(f"  Slots OK: {cluster_info.get('cluster_slots_ok', 'Unknown')}")
    except Exception as e:
        print(f"  Cluster info not available: {e}")

    # Connection info
    print("\n📊 Connection Information")
    info = client.info()
    print(f"  Redis Version: {info.get('redis_version', 'Unknown')}")
    print(f"  Connected Clients: {info.get('connected_clients', 'Unknown')}")
    print(f"  Used Memory: {info.get('used_memory_human', 'Unknown')}")

    print("\n✅ Cluster Redis example completed!")


if __name__ == "__main__":
    main()
