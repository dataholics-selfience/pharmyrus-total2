#!/bin/bash
# Pharmyrus API v4.2 - Railway Start Script

# Get PORT from environment or use default
PORT=${PORT:-8000}

echo "Starting Pharmyrus API v4.2 on port $PORT..."

# Start uvicorn with explicit port
exec uvicorn main_v4_2_production:app --host 0.0.0.0 --port $PORT
