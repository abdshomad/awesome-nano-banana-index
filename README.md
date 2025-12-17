# awesome-nano-banana-index

A curated collection and index of GitHub repositories related to **Nano Banana** (Gemini-2.5-Flash-Image) image generation and editing.

## Overview

This repository serves as a centralized index of awesome-nano-banana related GitHub repositories. The collection will be aggregated, collected, indexed, and made searchable through a web application, providing easy access to all Nano Banana-related projects, tools, prompts, and resources.

## Purpose

- **Aggregate**: Collect all Nano Banana related repositories in one place
- **Index**: Organize repositories for easy discovery
- **Search**: Enable quick search and filtering through a web interface
- **Discover**: Help users find relevant tools, prompts, and resources

## Search Engine

This repository includes a powerful search engine for indexing and searching all content from the submodules.

### Quick Start

#### Option 1: Using Shell Scripts (Recommended)

1. **Install and start services**:
   ```bash
   ./install.sh
   ```
   This will:
   - Initialize git submodules
   - Build Docker images (if needed)
   - Start all services in the background

2. **Run indexing** (if not auto-triggered):
   ```bash
   ./run-indexing.sh
   ```

3. **Access the web interface**:
   Open `http://localhost:8080` (or your configured port from `.env`)

#### Option 2: Manual Docker Commands

1. **Start the search engine**:
   ```bash
   docker compose up -d
   ```

2. **Build the search index**:
   ```bash
   docker compose exec fastapi uv run python -m search index
   ```

3. **Access the web interface**:
   Open `http://localhost:8080` (or your configured port)

#### Option 3: Run Locally (No Docker)

For Mac/Linux/Windows users who prefer to run directly:

1.  **Run the script**:
    ```bash
    ./run_local.sh
    ```
    This handles dependencies and starts the service.
    See [docs/RUN_WITHOUT_DOCKER.md](./docs/RUN_WITHOUT_DOCKER.md) for details.

### Management Scripts

The repository includes convenient shell scripts for managing the services:

#### Docker Services

- **`./install.sh`** - Install dependencies, build images, and start services
- **`./start.sh`** - Start all Docker services in background
- **`./stop.sh`** - Stop all Docker services
- **`./restart.sh`** - Restart all Docker services (stop then start)
- **`./run-indexing.sh`** - Run the indexing process in background
- **`./monitor.sh`** - Display real-time logs from all services (foreground)

#### Local Setup (No Docker)
- **`./run_local.sh`** - Run application locally (installs dependencies, manages Meilisearch)
- **`./update_submodules.sh`** - Update all submodules to latest remote versions

All scripts run in background except `monitor.sh`, which displays logs interactively.

### Features

- 🔍 **Full-text search** across all case files, prompts, and documentation
- 🌐 **Multilingual support** for Chinese and English content
- ⚡ **Fast search** powered by Meilisearch
- 💻 **CLI interface** for command-line usage
- 🎨 **Web interface** with modern UI and real-time search
- 🔗 **Direct links** to original repository files - click any result to open the file in its original GitHub repository
- 🐳 **Docker Compose** setup for easy deployment
- 📦 **Smart indexing** - prevents recreating index if it already exists

### Documentation

For detailed documentation on using the search engine, see [search/README.md](./search/README.md).

For Docker setup notes and troubleshooting, see [docs/DOCKER_SETUP.md](./docs/DOCKER_SETUP.md).

For running without Docker, see [docs/RUN_WITHOUT_DOCKER.md](./docs/RUN_WITHOUT_DOCKER.md).

## Repository List

See [repo-list.md](./repo-list.md) for the complete list of indexed repositories.

## Submodules

This repository uses Git submodules to include related awesome-nano-banana repositories. 

### Initial Setup

If you're cloning this repository for the first time, initialize and update the submodules:

```bash
git submodule update --init --recursive
```

Or clone with submodules in one command:

```bash
git clone --recurse-submodules <repository-url>
```

### Updating All Submodules

To update all submodules to their latest commits from their respective remote repositories, use the provided script:

```bash
./update_submodules.sh
```

This script handles the update process robustly, avoiding common "unrelated history" errors by resetting submodules to their remote state. It also triggers a search index update if the service is running.

### Updating to Committed Versions

To update all submodules to the specific commits referenced in this repository:

```bash
git submodule update --recursive
```


## Text-Based Database

A simple, version-controlled database of prompts is available in the `database/` directory. Each entry is a Markdown file with YAML frontmatter.

### Managing Entries

A helper script `manage_db.py` is provided to manage the database.

1. **List entries**:
   ```bash
   python manage_db.py list
   ```

2. **Add a new entry**:
   ```bash
   python manage_db.py add
   ```
   Follow the interactive prompts to create a new file.

3. **Validate entries**:
   ```bash
   python manage_db.py validate
   ```

4. **Extract from submodules**:
   ```bash
   python manage_db.py extract --source all
   ```
   This automates the population of the database from included submodules.

## Project Structure


```
awesome-nano-banana-index/
├── search/              # Search engine implementation
│   ├── README.md       # Search engine documentation
│   └── ...             # Search engine modules
├── docs/               # Additional documentation
│   ├── DOCKER_SETUP.md
│   └── future-enhancements.md
├── nginx/              # Nginx configuration
├── templates/          # Web UI templates
├── static/             # Static assets (CSS, JS)
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile          # FastAPI service Dockerfile
├── pyproject.toml      # Python dependencies (uv)
├── install.sh          # Installation script
├── start.sh            # Start services script
├── stop.sh             # Stop services script
├── restart.sh          # Restart services script
├── run-indexing.sh     # Run indexing script
├── run_local.sh        # Local run script (No Docker)
├── update_submodules.sh # Submodule update script
├── monitor.sh          # Monitor logs script
└── repo-list.md        # List of indexed repositories
```

## Contributing

Contributions are welcome! If you know of a Nano Banana related repository that should be included, please add it to [repo-list.md](./repo-list.md) or open an issue.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.