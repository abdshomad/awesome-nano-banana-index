# Run Without Docker

This guide explains how to run the Nano Banana Search Engine locally on your machine without using Docker.

## Prerequisites

Before starting, ensure you have the following installed:

1.  **Python 3.11+**:
    *   Verify with: `python3 --version`
2.  **uv** (Python package manager):
    *   Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
    *   Or follow instructions at: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
3.  **Meilisearch v1.0+**:
    *   **Mac (Homebrew)**: `brew install meilisearch`
    *   **Linux/WSL**: `curl -L https://install.meilisearch.com | sh`
    *   **Windows**: See [Meilisearch Documentation](https://www.meilisearch.com/docs/learn/self_hosted/install_meilisearch_locally)

## Quick Start (Script)

We have provided a helper script that automates the setup and execution process (except for installing system dependencies like Meilisearch).

1.  Open a new terminal and search engine:
    ```bash
    # Run in a separate terminal window
    meilisearch --master-key=dev_master_key_change_in_production
    ```
    *Note: The master key MUST match the one in the script/env (default: `dev_master_key_change_in_production`).*

2.  Run the local start script:
    ```bash
    ./run_local.sh
    ```
    This will:
    *   Install Python dependencies using `uv`.
    *   Trigger the indexing process.
    *   Start the web application at `http://localhost:8000`.

## Manual Setup

If you prefer to run commands manually:

### 1. Start Meilisearch

```bash
meilisearch --master-key=dev_master_key_change_in_production
```

### 2. Install Dependencies

```bash
uv sync 
```

### 3. Run Indexing

```bash
# Set environment variables
export MEILISEARCH_URL="http://localhost:7700"
export MEILISEARCH_API_KEY="dev_master_key_change_in_production"
export INDEX_NAME="nano_banana_index"

# Run the indexer
uv run python -m search index
```

### 4. Start the Web App

```bash
# Ensure environment variables are set (same as above)
export MEILISEARCH_URL="http://localhost:7700"
export MEILISEARCH_API_KEY="dev_master_key_change_in_production"
export INDEX_NAME="nano_banana_index"

# Run Uvicorn
uv run uvicorn search.web_app:app --host 0.0.0.0 --port 8000 --reload
```

## Troubleshooting

-   **"Connection refused"**: Ensure Meilisearch is running on port 7700.
-   **"Command not found: uv"**: Ensure `uv` is installed and in your PATH.
-   **Search not working**: Check the logs to see if indexing completed successfully.
