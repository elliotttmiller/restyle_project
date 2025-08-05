# File: backend/backend/urls.py

import os
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.utils import timezone
from .auth_views import token_obtain_pair, token_refresh, test_credentials

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

def test_endpoint(request):
    """Simple test endpoint to verify basic functionality"""
    return JsonResponse({
        "message": "Test endpoint working",
        "method": request.method,
        "path": request.path,
        "timestamp": timezone.now().isoformat()
    })

urlpatterns = [
    path('', project_root),
    path('health/', health_check),
    path('health', simple_health),  # Simple health check without trailing slash
    path('test/', test_endpoint),  # Simple test endpoint
    path('admin/', admin.site.urls),
    
    # CORRECTED: All user-related routes (register) now point to the 'users.urls'.
    path('api/users/', include('users.urls')), 
    
    # Custom authentication endpoints
    path('api/token/', token_obtain_pair, name='token_obtain_pair'),
    path('api/token/refresh/', token_refresh, name='token_refresh'),
    path('api/test-credentials/', test_credentials, name='test_credentials'),
    
    # All core business logic routes (items, analysis, etc.) point to 'core.urls'.
    # path('api/core/', include('core.urls')),  # Mount core app under /api/core/
]