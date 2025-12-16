#!/bin/bash

# start.sh - Start docker services in background

set -e

echo "Starting docker services in background..."

# Start services
docker compose up -d

# Wait a moment for services to start
sleep 5

# Check service status
echo "Service status:"
docker compose ps

echo ""
echo "Services started successfully!"
echo "Use './monitor.sh' to view logs or './stop.sh' to stop services."
