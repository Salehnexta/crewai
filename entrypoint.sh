#!/bin/sh
# Railway deployment entrypoint script
# Handles environment variable expansion properly

# Default port if not set
PORT=${PORT:-8000}

echo "Starting Morvo AI Platform on port: $PORT"

# Decide which API to run based on DEPLOYMENT_TIER env var
DEPLOYMENT_TIER=${DEPLOYMENT_TIER:-"minimal"}

case $DEPLOYMENT_TIER in
  "auth")
    echo "Starting Auth tier API on port: $PORT"
    exec uvicorn test_auth_api:app --host 0.0.0.0 --port $PORT
    ;;
  *)
    echo "Starting Minimal API on port: $PORT"
    exec uvicorn test_minimal_api:app --host 0.0.0.0 --port $PORT
    ;;
esac
