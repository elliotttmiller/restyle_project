from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.utils import timezone
import os
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# File: backend/backend/urls.py

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
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    # User and authentication endpoints
    path('api/users/', include('users.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Core API endpoints (all business logic, eBay, AI, etc.)
    path('api/core/', include('core.urls')),

    # Optionally, add a root health check or test endpoint if needed
    # path('health/', some_health_view),
]