# Search Engine Documentation

A powerful search engine for indexing and searching content from awesome-nano-banana-index repositories.

## Features

- **Full-text search** across all case files, prompts, and documentation
- **Multilingual support** for Chinese and English content
- **Fast search** powered by Meilisearch
- **CLI interface** for command-line usage
- **Web interface** with modern UI
- **Docker Compose** setup for easy deployment

## Architecture

The search engine consists of:

1. **Meilisearch Server** - Search engine backend (internal)
2. **FastAPI Application** - Web API and interface (internal)
3. **Nginx Reverse Proxy** - URL routing and single port exposure
4. **CLI Tool** - Command-line interface

## Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for CLI usage)

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd awesome-nano-banana-index
   ```

2. **Initialize submodules**:
   ```bash
   git submodule update --init --recursive
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env to set your preferred port
   ```

4. **Start services with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

5. **Build the search index**:
   ```bash
   # Using CLI (requires Python environment with uv)
   uv run python -m search index
   
   # Or using Docker
   docker-compose exec fastapi uv run python -m search index
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Docker Compose exposed port
EXPOSED_PORT=8080

# Meilisearch configuration
MEILISEARCH_URL=http://meilisearch:7700
MEILISEARCH_API_KEY=

# Application configuration
INDEX_NAME=nano_banana_index
SEARCH_RESULT_LIMIT=20
```

## Usage

### Web Interface

Once the services are running, access the web interface at:

```
http://localhost:8080
```

(Replace `8080` with the port specified in your `.env` file)

The web interface provides:
- Real-time search as you type
- Language filtering (Chinese, English, or both)
- Submodule filtering
- Results with titles, authors, prompts, and paths

### CLI Interface

#### Build Index

```bash
# Build index
uv run python -m search index

# Rebuild entire index
uv run python -m search index --rebuild
```

#### Search

```bash
# Basic search
uv run python -m search search "query"

# Search with language filter
uv run python -m search search "query" --lang en

# Search in specific submodule
uv run python -m search search "query" --submodule awesome-nano-banana-HildaM

# Search with pagination
uv run python -m search search "query" --limit 50 --offset 0
```

#### List Submodules

```bash
uv run python -m search list-submodules
```

#### Show Case Details

```bash
uv run python -m search show <case_id>
```

### API Endpoints

The FastAPI application provides REST API endpoints:

#### Search

```
GET /api/search?q=<query>&lang=<lang>&submodule=<name>&limit=<n>&offset=<n>
```

**Parameters:**
- `q` (required): Search query
- `lang` (optional): Language filter (`zh`, `en`, or `both`)
- `submodule` (optional): Filter by submodule name
- `limit` (optional): Number of results (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "hits": [
    {
      "id": "...",
      "title": "...",
      "title_en": "...",
      "prompt": "...",
      "prompt_en": "...",
      "author": "...",
      "submodule": "...",
      "path": "...",
      ...
    }
  ],
  "total": 100,
  "offset": 0,
  "limit": 20
}
```

#### Get Case by ID

```
GET /api/case/<case_id>
```

#### List Submodules

```
GET /api/submodules
```

**Response:**
```json
{
  "submodules": ["submodule1", "submodule2", ...]
}
```

#### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Development

### Local Development Setup

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Python dependencies**:
   ```bash
   uv sync
   ```

2. **Start Meilisearch** (using Docker Compose):
   ```bash
   docker-compose up -d meilisearch
   ```

3. **Run FastAPI locally**:
   ```bash
   uvicorn search.web_app:app --reload --port 8000
   ```

4. **Use CLI tools**:
   ```bash
   uv run python -m search index
   uv run python -m search search "query"
   ```

### Project Structure

```
awesome-nano-banana-index/
├── search/
│   ├── __init__.py
│   ├── indexer.py          # Content extraction and indexing
│   ├── search.py           # Meilisearch client wrapper
│   ├── cli.py              # CLI interface (Click)
│   ├── web_app.py          # FastAPI web application
│   ├── config.py           # Configuration
│   └── utils.py            # Helper functions
├── templates/              # HTML templates
│   └── index.html
├── static/                 # CSS/JS files
│   └── style.css
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # FastAPI service Dockerfile
├── nginx/                  # Nginx configuration
│   └── nginx.conf
├── pyproject.toml          # Python dependencies (uv)
└── search/README.md         # This file
```

## Troubleshooting

### Meilisearch Connection Error

If you see connection errors:
1. Check if Meilisearch is running: `docker-compose ps`
2. Check Meilisearch logs: `docker-compose logs meilisearch`
3. Verify `.env` file has correct `MEILISEARCH_URL`

### Index Not Found

If the index doesn't exist:
1. Run `python -m search index` to create and populate the index
2. Check that submodules are initialized: `git submodule status`

### Port Already in Use

If the exposed port is already in use:
1. Change `EXPOSED_PORT` in `.env` file
2. Restart services: `docker-compose down && docker-compose up -d`

## Maintenance

### Rebuilding Index

To rebuild the entire index:

```bash
uv run python -m search index --rebuild
```

### Updating Submodules

When submodules are updated:

```bash
git submodule update --remote --merge
python -m search index --rebuild
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi
docker-compose logs -f meilisearch
docker-compose logs -f nginx
```

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
