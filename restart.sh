#!/bin/bash

# restart.sh - Restart docker services in background

set -e

echo "Restarting docker services..."

# Stop services first
echo "Stopping services..."
docker compose down

# Wait a moment
sleep 2

# Start services
echo "Starting services..."
docker compose up -d

# Wait a moment for services to start
sleep 5

# Check service status
echo "Service status:"
docker compose ps

echo ""
echo "Services restarted successfully!"
echo "Use './monitor.sh' to view logs or './stop.sh' to stop services."
