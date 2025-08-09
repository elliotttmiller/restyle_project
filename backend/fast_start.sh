#!/bin/bash

# Fast Railway startup script - optimized for production
set -e

# Set library path for Nix libraries
export LD_LIBRARY_PATH=$(find /nix/store -type d -name lib 2>/dev/null | tr '\n' ':')$LD_LIBRARY_PATH

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "/opt/venv" ]; then
    source /opt/venv/bin/activate
fi

echo "🚀 Starting Restyle Backend (Optimized)"

# Environment check
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    exit 1
fi

# Skip database check for faster startup
echo "⏱️  Skipping database check for health endpoint..."

# Run migrations only if needed
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Start the Celery worker in the background
echo "🔄 Starting Celery worker..."
celery -A backend.celery_app worker --loglevel=info &

# Start optimized Gunicorn
echo "🌟 Starting Gunicorn server..."
echo "🌐 Server starting on port $PORT"

exec gunicorn backend.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class sync \
    --timeout 60 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -