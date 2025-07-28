#!/usr/bin/env python3
"""
Sentinel Redis Example - Asynchronous

This example demonstrates how to use python-redis-factory with Redis Sentinel
in asynchronous mode.
"""

import asyncio

from python_redis_factory import get_redis_client


async def main():
    """Main function demonstrating Sentinel Redis usage."""
    print("🚀 Sentinel Redis - Asynchronous Example")
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

    client = get_redis_client(sentinel_uri, async_client=True)

    # Basic operations
    print("🔧 Basic Redis Operations")

    # String operations
    await client.set("greeting", "Hello from Sentinel!")
    greeting = await client.get("greeting")
    print(f"  Set/Get: {greeting}")

    # List operations
    await client.lpush("items", "item1", "item2", "item3")
    items = await client.lrange("items", 0, -1)
    print(f"  List: {items}")

    # Hash operations
    await client.hset(
        "user:1", mapping={"name": "Alice", "age": "30", "city": "New York"}
    )
    user = await client.hgetall("user:1")
    print(f"  Hash: {user}")

    # Set operations
    await client.sadd("tags", "python", "redis", "sentinel", "high-availability")
    tags = await client.smembers("tags")
    print(f"  Set: {tags}")

    # Sorted set operations
    await client.zadd("scores", {"Alice": 100, "Bob": 85, "Charlie": 95})
    top_scores = await client.zrevrange("scores", 0, 2, withscores=True)
    print(f"  Sorted Set: {top_scores}")

    # Concurrent operations
    print("\n⚡ Concurrent Operations")
    tasks = []
    for i in range(5):
        task = client.set(f"concurrent:{i}", f"value-{i}")
        tasks.append(task)

    await asyncio.gather(*tasks)
    print("  Concurrent set operations completed")

    # Fetch all values concurrently
    fetch_tasks = []
    for i in range(5):
        task = client.get(f"concurrent:{i}")
        fetch_tasks.append(task)

    results = await asyncio.gather(*fetch_tasks)
    print(f"  Concurrent results: {results}")

    # Replication info
    print("\n📊 Replication Information")
    info = await client.info("replication")
    print(f"  Role: {info.get('role', 'Unknown')}")
    print(f"  Connected Slaves: {info.get('connected_slaves', 'Unknown')}")

    # Connection info
    print("\n📊 Connection Information")
    info = await client.info()
    print(f"  Redis Version: {info.get('redis_version', 'Unknown')}")
    print(f"  Connected Clients: {info.get('connected_clients', 'Unknown')}")
    print(f"  Used Memory: {info.get('used_memory_human', 'Unknown')}")

    print("\n✅ Sentinel Redis example completed!")


if __name__ == "__main__":
    asyncio.run(main())
