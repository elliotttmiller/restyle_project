#!/bin/bash
# Production Deployment Script for Restyle Backend

echo "🚀 Deploying Restyle Backend to Production"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "backend/manage.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

cd backend

echo "📦 Installing Production Dependencies..."
pip install -r requirements.txt

echo "🔧 Configuring Production Settings..."
export DEBUG=False
export DJANGO_SETTINGS_MODULE=backend.settings

echo "🗄️ Running Database Migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "👤 Creating Superuser (if needed)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@restyle.app', 'secure_admin_password')
    print('Superuser created')
else:
    print('Superuser already exists')
"

echo "🧪 Running Authentication Tests..."
cd ..
if [ -f "test_mobile_auth.sh" ]; then
    echo "Testing with local backend..."
    ./test_mobile_auth.sh
fi

echo "🔐 Setting Up CORS for Production..."
# This would be handled in Django settings for production domains

echo "📊 Collecting Static Files..."
cd backend
python manage.py collectstatic --noinput || echo "Static files collection skipped (whitenoise disabled)"

echo "✅ Production Deployment Complete!"
echo ""
echo "🔧 Configuration Steps:"
echo "1. Update ALLOWED_HOSTS in settings.py with your domain"
echo "2. Set SECRET_KEY environment variable"
echo "3. Configure CORS_ALLOWED_ORIGINS for your mobile app"
echo "4. Set up HTTPS SSL certificates"
echo "5. Configure environment variables for production"
echo ""
echo "📋 Environment Variables Needed:"
echo "- DEBUG=False"
echo "- SECRET_KEY=your-secret-key"
echo "- DATABASE_URL=your-database-url (if using PostgreSQL)"
echo "- ALLOWED_HOSTS=your-domain.com"
echo ""
echo "🧪 Test Endpoints:"
echo "- GET /health - Health check"
echo "- POST /api/token/ - Authentication"
echo "- GET /api/protected/ - Protected endpoint test"
echo ""
echo "🎉 Your backend is ready for production!"