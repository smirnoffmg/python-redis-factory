#!/usr/bin/env python3
"""
Cluster Redis Example - Asynchronous

This example demonstrates how to use python-redis-factory with Redis Cluster
in asynchronous mode.
"""

import asyncio
import os

from python_redis_factory import get_redis_client


async def main():
    """Main function demonstrating Cluster Redis usage."""
    print("🚀 Cluster Redis - Asynchronous Example")
    print("=" * 50)

    # Connect to Redis Cluster
    # Use internal hostnames when running inside Docker, external when outside
    if os.path.exists("/.dockerenv"):
        # Running inside Docker container
        cluster_uri = "redis+cluster://:redis123@redis-cluster-1:6379,redis-cluster-2:6379,redis-cluster-3:6379,redis-cluster-4:6379,redis-cluster-5:6379,redis-cluster-6:6379"
    else:
        # Running outside Docker
        cluster_uri = "redis+cluster://:redis123@localhost:7001,localhost:7002,localhost:7003,localhost:7004,localhost:7005,localhost:7006"

    print(f"🔗 Connecting to Redis Cluster: {cluster_uri}")
    client = get_redis_client(cluster_uri, async_client=True)

    # Test cluster-specific operations
    print("\n🔧 Cluster-Specific Operations")

    # Cluster info
    print("📊 Cluster Information")
    try:
        cluster_info = await client.cluster_info()
        print(f"  Cluster State: {cluster_info.get('cluster_state', 'Unknown')}")
        print(
            f"  Slots Assigned: {cluster_info.get('cluster_slots_assigned', 'Unknown')}"
        )
        print(f"  Slots OK: {cluster_info.get('cluster_slots_ok', 'Unknown')}")
        print(f"  Slots PFail: {cluster_info.get('cluster_slots_pfail', 'Unknown')}")
        print(f"  Slots Fail: {cluster_info.get('cluster_slots_fail', 'Unknown')}")
        print(f"  Known Nodes: {cluster_info.get('cluster_known_nodes', 'Unknown')}")
        print(f"  Size: {cluster_info.get('cluster_size', 'Unknown')}")
    except Exception as e:
        print(f"  ❌ Cluster info not available: {e}")

    # Cluster nodes
    print("\n📋 Cluster Nodes")
    try:
        nodes = await client.cluster_nodes()
        print(f"  Total Nodes: {len(nodes)}")
        for node_id, node_info in nodes.items():
            role = node_info.get("flags", "unknown")
            host_port = (
                f"{node_info.get('host', 'unknown')}:{node_info.get('port', 'unknown')}"
            )
            print(f"    {node_id[:8]}... - {host_port} ({role})")
    except Exception as e:
        print(f"  ❌ Cluster nodes not available: {e}")

    # Cluster slots
    print("\n🎯 Cluster Slots")
    try:
        slots = await client.cluster_slots()
        print(f"  Total Slots: {len(slots)}")
        for slot_range, nodes in slots.items():
            start, end = slot_range
            master = nodes[0] if nodes else None
            if master:
                print(f"    Slots {start}-{end}: {master['host']}:{master['port']}")
    except Exception as e:
        print(f"  ❌ Cluster slots not available: {e}")

    # Basic operations (these will be distributed across the cluster)
    print("\n🔧 Basic Redis Operations (Distributed)")

    # String operations
    await client.set("greeting", "Hello from Cluster!")
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
    await client.sadd("tags", "python", "redis", "cluster", "distributed")
    tags = await client.smembers("tags")
    print(f"  Set: {tags}")

    # Sorted set operations
    await client.zadd("scores", {"Alice": 100, "Bob": 85, "Charlie": 95})
    top_scores = await client.zrevrange("scores", 0, 2, withscores=True)
    print(f"  Sorted Set: {top_scores}")

    # Test key distribution across cluster
    print("\n🎲 Testing Key Distribution")
    for i in range(10):
        key = f"distributed_key_{i}"
        await client.set(key, f"value_{i}")
        value = await client.get(key)
        print(f"  {key}: {value}")

    # Concurrent operations across cluster
    print("\n⚡ Concurrent Operations (Distributed)")
    tasks = []
    for i in range(10):
        task = client.set(f"concurrent_cluster_{i}", f"cluster_value_{i}")
        tasks.append(task)

    await asyncio.gather(*tasks)
    print("  Concurrent set operations completed")

    # Fetch all values concurrently
    fetch_tasks = []
    for i in range(10):
        task = client.get(f"concurrent_cluster_{i}")
        fetch_tasks.append(task)

    results = await asyncio.gather(*fetch_tasks)
    print(f"  Concurrent results: {results}")

    # Connection info
    print("\n📊 Connection Information")
    try:
        info = await client.info()
        print(f"  Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"  Connected Clients: {info.get('connected_clients', 'Unknown')}")
        print(f"  Used Memory: {info.get('used_memory_human', 'Unknown')}")
    except Exception as e:
        print(f"  ❌ Connection info not available: {e}")

    print("\n✅ Cluster Redis example completed!")


if __name__ == "__main__":
    asyncio.run(main())
