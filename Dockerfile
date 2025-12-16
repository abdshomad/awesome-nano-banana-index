FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN chmod +x /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies using uv
# Use --no-dev to skip dev dependencies in production
RUN uv sync --no-dev

# Copy application code
COPY . .

# Expose port (though it won't be directly exposed, only through nginx)
EXPOSE 8000

# Run FastAPI application using uv
CMD ["uv", "run", "uvicorn", "search.web_app:app", "--host", "0.0.0.0", "--port", "8000"]
