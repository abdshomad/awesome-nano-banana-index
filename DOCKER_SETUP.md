# Docker Setup Notes

## Fixed Issues

1. **Dockerfile**: Removed `--frozen` flag from `uv sync` since we don't have a lock file yet
2. **docker-compose.yml**: 
   - Added `working_dir` to FastAPI service
   - Added proper health check dependency for FastAPI on Meilisearch
   - Added `restart: unless-stopped` to all services
   - Added `start_period` to Meilisearch healthcheck
3. **nginx.conf**: Added `proxy_read_timeout` for long-running requests

## Testing

To test the setup:

```bash
# Start services
docker compose up -d

# Check logs
docker compose logs -f

# Check service status
docker compose ps

# Stop services
docker compose down
```

## Potential Issues

### Meilisearch Healthcheck

If the Meilisearch healthcheck fails, it might be because curl is not available in the image. You can:

1. Remove the healthcheck temporarily
2. Or modify it to use a different tool that's available in the image

The Meilisearch image is minimal, so if curl doesn't work, you may need to:
- Use a different healthcheck method
- Or rely on the service's own health endpoint without curl

### UV Sync

The first build will create a lock file. Subsequent builds can use `--frozen` flag for faster, reproducible builds.

To generate a lock file:
```bash
uv lock
```

Then update Dockerfile to use:
```dockerfile
RUN uv sync --frozen --no-dev
```
