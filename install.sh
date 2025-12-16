#!/bin/bash

# install.sh - Install and setup dependencies for the docker services

set -e

echo "Installing dependencies and setting up docker services..."

# Initialize git submodules if not already done
if [ -f .gitmodules ]; then
    echo "Initializing git submodules..."
    git submodule update --init --recursive
fi

# Build docker images only if they don't exist
echo "Checking if docker images need to be built..."
if docker images | grep -q "awesome-nano-banana-index-fastapi"; then
    echo "Docker images already exist. Skipping build."
else
    echo "Building docker images..."
    docker compose build
fi

# Start services in background
echo "Starting docker services..."
docker compose up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Check service status
echo "Checking service status..."
docker compose ps

echo "Installation complete!"
echo "Services are running in the background."
echo "Use './monitor.sh' to view logs or './stop.sh' to stop services."
