#!/bin/bash

# Re-Style Local Development Startup Script (No Docker)

echo "🚀 Starting Re-Style Local Development Environment..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Update Django settings for local development
echo "⚙️  Updating Django settings for local development..."
cat > backend/local_settings.py << EOF
# Local development settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable Celery for local development
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'rpc://'

# eBay API settings (you'll need to add your own)
EBAY_APP_ID = "Your-App-ID-Goes-Here"
EOF

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

# Start Django development server
echo "🌐 Starting Django development server..."
python manage.py runserver 8000 &

# Wait a moment for Django to start
sleep 3

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd ../frontend
npm install

# Start React development server
echo "⚛️  Starting React development server..."
npm start &

echo "✅ Local development environment started!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "👤 Admin login: admin/admin123"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop
wait 
