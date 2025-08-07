#!/bin/bash

# Fast Railway startup script - optimized for production
set -e

# Activate virtual environment
source /opt/venv/bin/activate

echo "🚀 Starting Restyle Backend (Optimized)"

# Environment check
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    exit 1
fi

# Quick database check (reduced timeout)
echo "⏱️  Checking database connection..."
python -c "
import os, psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print('✅ Database connected')
except Exception as e:
    print(f'❌ Database error: {e}')
    exit(1)
"

# Run migrations only if needed
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

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
