"""
Authentication middleware for verifying tokens in API requests
"""
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from backend.auth_views import verify_token
import functools

User = get_user_model()

def require_auth(view_func):
    """
    Decorator to require authentication for API views
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                'error': 'Authentication required',
                'detail': 'No valid authentication token provided'
            }, status=401)
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return JsonResponse({
                'error': 'Invalid token',
                'detail': 'Token is invalid or expired'
            }, status=401)
        
        # Get user
        try:
            user = User.objects.get(id=payload['user_id'])
            if not user.is_active:
                return JsonResponse({
                    'error': 'User account disabled',
                    'detail': 'User account is not active'
                }, status=401)
        except User.DoesNotExist:
            return JsonResponse({
                'error': 'User not found',
                'detail': 'User associated with token does not exist'
            }, status=401)
        
        # Add user to request
        request.user = user
        
        return view_func(request, *args, **kwargs)
    
    return wrapper