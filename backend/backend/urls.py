# File: backend/backend/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse
from django.utils import timezone

def project_root(request):
    return JsonResponse({
        "status": "healthy",
        "message": "Welcome to the Restyle API! The backend is running.",
        "timestamp": timezone.now().isoformat()
    })

def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "service": "restyle-backend",
        "timestamp": timezone.now().isoformat()
    })

urlpatterns = [
    path('', project_root),
    path('health/', health_check),
    path('admin/', admin.site.urls),
    # path('', include('core.urls')),  # Commented out root-level include
    
    # CORRECTED: All user-related routes (register) now point to the 'users.urls'.
    path('api/users/', include('users.urls')), 
    
    # Token (login) routes remain here as they are from a third-party app.
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # All core business logic routes (items, analysis, etc.) point to 'core.urls'.
    path('api/core/', include('core.urls')),  # Mount core app under /api/core/
]