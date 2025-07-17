# File: backend/backend/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Add this line to include core.urls at the root
    
    # CORRECTED: All user-related routes (register) now point to the 'users.urls'.
    path('api/users/', include('users.urls')), 
    
    # Token (login) routes remain here as they are from a third-party app.
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # All core business logic routes (items, analysis, etc.) point to 'core.urls'.
    path('api/core/', include('core.urls')),
]