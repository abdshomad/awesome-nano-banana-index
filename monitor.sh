#!/bin/bash

# monitor.sh - Display real-time logs from docker services

set -e

# Display real-time logs from all services
# This script runs in foreground to show logs interactively
docker compose logs -f
