#!/bin/bash

# run-indexing.sh - Run the indexing process in the docker container (background)

set -e

echo "Starting indexing process in background..."

# Check if services are running
if ! docker compose ps fastapi 2>/dev/null | grep -q "Up"; then
    echo "Error: FastAPI service is not running. Please start services first with './start.sh'"
    exit 1
fi

# Run indexing in background
docker compose exec -d fastapi uv run python -m search index

echo "Indexing process started in background."
echo "Use './monitor.sh' to view indexing progress."
