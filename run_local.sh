#!/bin/bash

# run_local.sh - Run the application locally without Docker

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Nano Banana Search Engine (Local Mode)${NC}"

# Check for prerequisites
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: 'uv' is not installed.${NC}"
    echo "Please install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

MEILISEARCH_PID=""

# Function to cleanup background processes
cleanup() {
    if [ -n "$MEILISEARCH_PID" ]; then
        echo -e "\n${YELLOW}Stopping Meilisearch (PID: $MEILISEARCH_PID)...${NC}"
        kill "$MEILISEARCH_PID" 2>/dev/null || true
    fi
    exit 0
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM EXIT

# Check if Meilisearch is running
echo -e "${YELLOW}Checking Meilisearch status...${NC}"
if curl -s http://localhost:7700/health > /dev/null; then
    echo -e "${GREEN}Meilisearch is already running.${NC}"
else
    echo -e "${YELLOW}Meilisearch not running. Starting it...${NC}"
    
    # Check if meilisearch is installed
    if ! command -v meilisearch &> /dev/null; then
        echo -e "${RED}Error: 'meilisearch' command not found.${NC}"
        echo "Please install Meilisearch first (see docs/RUN_WITHOUT_DOCKER.md)"
        exit 1
    fi

    # Start Meilisearch in background
    meilisearch --master-key=dev_master_key_change_in_production > /dev/null 2>&1 &
    MEILISEARCH_PID=$!
    
    # Wait for Meilisearch to be ready
    echo -e "${YELLOW}Waiting for Meilisearch to be ready...${NC}"
    MAX_RETRIES=10
    COUNT=0
    while ! curl -s http://localhost:7700/health > /dev/null; do
        sleep 1
        COUNT=$((COUNT+1))
        if [ $COUNT -ge $MAX_RETRIES ]; then
            echo -e "${RED}Error: Timed out waiting for Meilisearch to start.${NC}"
            exit 1
        fi
    done
    echo -e "${GREEN}Meilisearch started successfully!${NC}"
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies with uv...${NC}"
uv sync

# Set environment variables
export MEILISEARCH_URL="http://localhost:7700"
export MEILISEARCH_API_KEY="dev_master_key_change_in_production"
export INDEX_NAME="nano_banana_index"

# Run indexing
echo -e "${YELLOW}Running search indexer...${NC}"
uv run python -m search index

# Start the web server
echo -e "${GREEN}Starting web server...${NC}"
echo -e "Access the app at: ${GREEN}http://localhost:8000${NC}"
echo -e "Press Ctrl+C to stop."

uv run uvicorn search.web_app:app --host 0.0.0.0 --port 8000 --reload
