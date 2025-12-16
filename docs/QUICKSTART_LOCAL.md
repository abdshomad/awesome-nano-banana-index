# Quickstart (Local)

Follow the instructions for your operating system.

## Mac / Linux

### Option 1: One-Click Run (Recommended)
```bash
./run_local.sh
```
*Meilisearch will start automatically.*

### Option 2: Manual (Multi-Terminal)
Terminal 1:
```bash
meilisearch --master-key=dev_master_key_change_in_production
```
Terminal 2:
```bash
./run_local.sh
```

## Windows (PowerShell)

### Terminal 1 (Search Engine)
```powershell
# Ensure meilisearch.exe is in your path or current directory
meilisearch --master-key=dev_master_key_change_in_production
```

### Terminal 2 (Application)
```powershell
# Install dependencies
uv sync

# Set environment variables
$env:MEILISEARCH_URL="http://localhost:7700"
$env:MEILISEARCH_API_KEY="dev_master_key_change_in_production"
$env:INDEX_NAME="nano_banana_index"

# Run indexing
uv run python -m search index

# Start the web server
uv run uvicorn search.web_app:app --host 0.0.0.0 --port 8000 --reload
```

---
**Access the app at:** http://localhost:8000
