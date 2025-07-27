#!/usr/bin/env python3
"""
Example usage of the Python Redis Factory.

This demonstrates the URI parsing, configuration management, and standalone client functionality.
"""

from unittest.mock import Mock, patch

from python_redis_factory import (
    RedisConnectionMode,
    create_config_from_uri,
    create_redis_client,
    get_default_config,
    get_redis_client,
    merge_configs,
    parse_redis_uri,
)


def main():
    """Demonstrate the Redis URI parsing and configuration management functionality."""
    print("🧱 Python Redis Factory - Simple API Demo")
    print("=" * 60)

    # Example URIs
    uris = [
        "redis://localhost:6379",
        "redis://:password@localhost:6379/1",
        "redis+sentinel://sentinel1:26379,sentinel2:26379/mymaster",
        "redis+cluster://node1:7000,node2:7001,node3:7002",
        "rediss://localhost:6379",  # SSL
    ]

    print("\n📝 URI Parsing Examples:")
    print("-" * 30)
    for uri in uris:
        print(f"\n🔗 Parsing: {uri}")
        try:
            config = parse_redis_uri(uri)
            print(f"   ✅ Mode: {config.mode.value}")
            print(f"   ✅ Host: {config.host}")
            print(f"   ✅ Port: {config.port}")
            print(f"   ✅ Database: {config.db}")
            print(f"   ✅ SSL: {config.ssl}")

            if config.mode == RedisConnectionMode.SENTINEL:
                print(f"   ✅ Sentinel Hosts: {config.sentinel_hosts}")
                print(f"   ✅ Service Name: {config.service_name}")
            elif config.mode == RedisConnectionMode.CLUSTER:
                print(f"   ✅ Cluster Nodes: {config.cluster_nodes}")

        except ValueError as e:
            print(f"   ❌ Error: {e}")

    print("\n⚙️  Configuration Management Examples:")
    print("-" * 40)

    # Default configurations
    print("\n🔧 Default Configurations:")
    standalone_default = get_default_config()
    sentinel_default = get_default_config(RedisConnectionMode.SENTINEL)
    cluster_default = get_default_config(RedisConnectionMode.CLUSTER)

    print(f"   Standalone: {standalone_default.host}:{standalone_default.port}")
    print(f"   Sentinel: {sentinel_default.mode.value} mode")
    print(f"   Cluster: {cluster_default.mode.value} mode")

    # Configuration with overrides
    print("\n🔧 Configuration with Overrides:")
    config_with_overrides = create_config_from_uri(
        "redis://localhost:6379",
        max_connections=20,
        socket_timeout=10.0,
        password="override_password",
    )
    print(f"   Max Connections: {config_with_overrides.max_connections}")
    print(f"   Socket Timeout: {config_with_overrides.socket_timeout}")
    print(f"   Password: {config_with_overrides.password}")

    # Configuration merging
    print("\n🔧 Configuration Merging:")
    base_config = get_default_config()
    override_config = get_default_config()
    override_config.host = "redis.example.com"
    override_config.port = 6380
    override_config.max_connections = 30

    merged_config = merge_configs(base_config, override_config)
    print(f"   Merged Host: {merged_config.host}")
    print(f"   Merged Port: {merged_config.port}")
    print(f"   Merged Max Connections: {merged_config.max_connections}")

    print("\n🔌 Standalone Client Creation:")
    print("-" * 30)

    # Create a standalone client
    config = create_config_from_uri("redis://localhost:6379")

    with patch("redis.Redis") as mock_redis:
        mock_instance = Mock()
        mock_redis.return_value = mock_instance
        mock_instance.ping.return_value = True
        mock_instance.set.return_value = True
        mock_instance.get.return_value = "demo_value"

        # Create client through factory
        client = create_redis_client(config)

        print(f"   ✅ Created client for: {config.host}:{config.port}")
        print(f"   ✅ Client type: {type(client).__name__}")

        # Test basic operations
        print(f"   ✅ Ping test: {client.ping()}")
        print(f"   ✅ Set operation: {client.set('demo_key', 'demo_value')}")
        print(f"   ✅ Get operation: {client.get('demo_key')}")

    print("\n🚀 Simple API Demo:")
    print("-" * 30)

    # Demonstrate the simple API
    with patch("redis.Redis") as mock_redis:
        mock_instance = Mock()
        mock_redis.return_value = mock_instance
        mock_instance.ping.return_value = True
        mock_instance.set.return_value = True
        mock_instance.get.return_value = "simple_api_value"

        # Simple one-liner client creation
        client = get_redis_client("redis://localhost:6379")

        print("   ✅ Simple API: get_redis_client('redis://localhost:6379')")
        print(f"   ✅ Client type: {type(client).__name__}")
        print(f"   ✅ Ping test: {client.ping()}")

        # Test with password
        get_redis_client("redis://:secret@localhost:6379")
        print("   ✅ With password: get_redis_client('redis://:secret@localhost:6379')")

        # Test with database selection
        get_redis_client("redis://localhost:6379/1")
        print("   ✅ With database: get_redis_client('redis://localhost:6379/1')")

        # Test with SSL
        get_redis_client("rediss://localhost:6379")
        print("   ✅ With SSL: get_redis_client('rediss://localhost:6379')")

        # Test with Sentinel
        get_redis_client("redis+sentinel://sentinel1:26379/mymaster")
        print(
            "   ✅ With Sentinel: get_redis_client('redis+sentinel://sentinel1:26379/mymaster')"
        )

    print("\n🎉 Simple API demo completed!")


if __name__ == "__main__":
    main()
