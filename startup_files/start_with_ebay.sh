#!/bin/bash

# Re-Style Development Startup Script with eBay Integration

echo "🚀 Starting Re-Style Development Environment with eBay Integration..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start Redis for Celery
echo "📦 Starting Redis for Celery..."
docker run -d --name redis-ebay -p 6379:6379 redis:7-alpine

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
sleep 5

# Start backend services
echo "📦 Starting backend services..."
cd backend

# Run Django migrations
echo "🔄 Running Django migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating superuser (if needed)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Start Celery worker
echo "🔧 Starting Celery worker..."
celery -A backend worker -l info &

# Start Django development server
echo "🌐 Starting Django development server..."
python manage.py runserver 8000 &

# Wait a moment for Django to start
sleep 5

# Start frontend
echo "⚛️  Starting React development server..."
cd ../frontend
npm start &

echo "✅ Development environment started with eBay integration!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "👤 Admin login: admin/admin123"
echo "🔧 Celery worker: Running in background"
echo "📦 Redis: Running on localhost:6379"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop
wait 