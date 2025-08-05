# File: backend/backend/urls.py

import os
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.utils import timezone
from .auth_views import token_obtain_pair, token_refresh, test_credentials

from django.http import JsonResponse
from django.utils import timezone
from .auth_views import token_obtain_pair, token_refresh, test_credentials
from .auth_middleware import require_auth

def project_root(request):
    return JsonResponse({
        "status": "healthy",
        "message": "Welcome to the Restyle API! The backend is running.",
        "timestamp": timezone.now().isoformat(),
        "debug": os.environ.get('DEBUG', 'False'),
        "port": os.environ.get('PORT', '8000')
    })

def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "service": "restyle-backend",
        "timestamp": timezone.now().isoformat()
    })

def simple_health(request):
    """Ultra-simple health check for Railway"""
    return JsonResponse({
        "status": "healthy",
        "service": "restyle-backend",
        "timestamp": timezone.now().isoformat(),
        "version": "1.0.0"
    })

def health(request):
    """Health check endpoint that returns exactly {"status": "ok"} for Railway"""
    return JsonResponse({"status": "ok"})

def test_endpoint(request):
    """Simple test endpoint to verify basic functionality"""
    return JsonResponse({
        "message": "Test endpoint working",
        "method": request.method,
        "path": request.path,
        "timestamp": timezone.now().isoformat()
    })

@require_auth
def protected_endpoint(request):
    """Test protected endpoint that requires authentication"""
    return JsonResponse({
        "message": "You are authenticated!",
        "user": {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email
        },
        "timestamp": timezone.now().isoformat()
    })

@require_auth
def user_profile(request):
    """Get user profile information"""
    return JsonResponse({
        "profile": {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "is_active": request.user.is_active,
            "date_joined": request.user.date_joined.isoformat(),
            "last_login": request.user.last_login.isoformat() if request.user.last_login else None
        },
        "timestamp": timezone.now().isoformat()
    })

urlpatterns = [
    path('', project_root),
    path('health/', health_check),
    path('health', simple_health),  # Simple health check without trailing slash
    path('health-ok/', health),  # Exact format health check for Railway
    path('test/', test_endpoint),  # Simple test endpoint
    path('admin/', admin.site.urls),
    
    # CORRECTED: All user-related routes (register) now point to the 'users.urls'.
    path('api/users/', include('users.urls')), 
    
    # Custom authentication endpoints
    path('api/token/', token_obtain_pair, name='token_obtain_pair'),
    path('api/token/refresh/', token_refresh, name='token_refresh'),
    path('api/test-credentials/', test_credentials, name='test_credentials'),
    
    # Protected endpoints for testing
    path('api/protected/', protected_endpoint, name='protected_endpoint'),
    path('api/profile/', user_profile, name='user_profile'),
    
    # All core business logic routes (items, analysis, etc.) point to 'core.urls'.
    # path('api/core/', include('core.urls')),  # Mount core app under /api/core/
]