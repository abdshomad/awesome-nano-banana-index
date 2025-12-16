#!/bin/bash

# update_submodules.sh - Update all submodules to the latest remote commit
# This script forcefully resets submodules to the tip of their remote default branch.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting submodule update...${NC}"

# Sync submodule URLs in case they changed in .gitmodules
echo -e "${YELLOW}Syncing submodule configurations...${NC}"
git submodule sync --recursive

# Update each submodule
echo -e "${YELLOW}Fetching and resetting submodules...${NC}"

git submodule foreach --recursive '
    echo "Processing $name..."
    
    # Fetch latest from origin
    git fetch origin
    
    # Attempt to detect default branch
    BRANCH=$(git remote show origin | grep "HEAD branch" | sed "s/.*: //")
    
    if [ -z "$BRANCH" ]; then
        # Fallback if detection fails
        echo "  Could not detect default branch, trying master..."
        BRANCH="master"
    fi
    
    echo "  Resetting to origin/$BRANCH..."
    git reset --hard origin/$BRANCH
'

echo -e "${GREEN}All submodules updated successfully!${NC}"

# Update Search Index
echo -e "\n${YELLOW}Checking Search Index...${NC}"

if curl -s http://localhost:7700/health > /dev/null; then
    echo -e "${GREEN}Meilisearch is running. Updating index...${NC}"
    
    # Set environment variables
    export MEILISEARCH_URL="http://localhost:7700"
    export MEILISEARCH_API_KEY="dev_master_key_change_in_production"
    export INDEX_NAME="nano_banana_index"
    
    # Run indexing
    if command -v uv &> /dev/null; then
        uv run python -m search index
        echo -e "${GREEN}Index update completed!${NC}"
    else
        echo -e "${RED}Error: 'uv' not found. Cannot run indexer.${NC}"
    fi
else
    echo -e "${YELLOW}Warning: Meilisearch is not running (checked http://localhost:7700).${NC}"
    echo -e "Skipping index update. Run './run_local.sh' later to update the index."
fi
