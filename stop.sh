#!/bin/bash

# stop.sh - Stop docker services

set -e

echo "Stopping docker services..."

# Stop services
docker compose down

echo "Services stopped successfully!"
