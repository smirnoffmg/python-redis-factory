#!/bin/bash

echo "🚀 Running Redis Standalone Examples"
echo "===================================="

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker compose down

# Start the Redis services
echo "🏗️  Starting Redis Standalone service..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Run examples
echo "🧪 Running examples..."
echo ""

# Run sync example
echo "📋 Running Sync Example:"
python sync_example.py

echo ""

# Run async example
echo "📋 Running Async Example:"
python async_example.py

echo ""
echo "✅ All examples completed!"

# Clean up
echo ""
echo "🧹 Cleaning up..."
docker compose down
echo "✅ Cleanup completed!" 