#!/bin/sh
# Railway deployment entrypoint script
# Handles environment variable expansion properly

# Default port if not set
PORT=${PORT:-8000}

echo "Starting Morvo AI Platform on port: $PORT"

# Run the application with the expanded PORT
exec uvicorn test_minimal_api:app --host 0.0.0.0 --port $PORT
