#!/bin/sh
set -e

echo "Running Alembic migrations..."
cd /app && python -m alembic upgrade head

echo "Starting application..."
exec uvicorn main:app --app-dir src --host 0.0.0.0 --port 8000
