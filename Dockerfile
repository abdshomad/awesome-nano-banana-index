FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN chmod +x /usr/local/bin/uv

# Copy dependency files and package source
COPY pyproject.toml README.md ./
COPY search/ ./search/

# Install Python dependencies using uv
# Use --no-dev to skip dev dependencies in production
RUN uv sync --no-dev

# Copy application code
COPY . .

# Expose port (though it won't be directly exposed, only through nginx)
EXPOSE 8000

# Run search indexer, start file watcher in background, then start HTTP server
CMD ["sh", "-c", "uv run python -m search index && uv run python watch_and_index.py & python3 -m http.server 8000"]
