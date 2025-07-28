#!/bin/bash

echo "🚀 Running Redis Sentinel Examples"
echo "=================================="

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker compose down

# Start the Redis services
echo "🏗️  Starting Redis Sentinel services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 1

# Run examples inside Docker network
echo "🧪 Running examples inside Docker network..."
echo ""

# Run sync example
echo "📋 Running Sync Example:"
docker run --rm \
  --network sentinel_redis-net \
  -v "$(pwd)/../..:/app" \
  -w /app \
  python:3.12-slim \
  sh -c "pip install -e . && python examples/sentinel/sync_example.py"

echo ""

# Run async example
echo "📋 Running Async Example:"
docker run --rm \
  --network sentinel_redis-net \
  -v "$(pwd)/../..:/app" \
  -w /app \
  python:3.12-slim \
  sh -c "pip install -e . && python examples/sentinel/async_example.py"

echo ""
echo "✅ All examples completed!"

# Clean up
echo ""
echo "🧹 Cleaning up..."
docker compose down
echo "✅ Cleanup completed!" 