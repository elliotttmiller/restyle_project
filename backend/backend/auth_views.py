"""
Custom authentication views for the Restyle backend
"""
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime, timedelta
import hashlib
import hmac
import base64


def create_token(user_id, username):
    """Create a simple token for authentication"""
    import time
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': int(time.time()) + (24 * 60 * 60),  # 24 hours
        'iat': int(time.time())
    }
    
    # Simple token creation (not production-ready JWT)
    token_data = json.dumps(payload)
    secret = "your-secret-key-here"  # Should be in settings
    signature = hmac.new(secret.encode(), token_data.encode(), hashlib.sha256).hexdigest()
    token = base64.b64encode(f"{token_data}.{signature}".encode()).decode()
    
    return token


def verify_token(token):
    """Verify a simple token"""
    try:
        decoded = base64.b64decode(token.encode()).decode()
        token_data, signature = decoded.rsplit('.', 1)
        
        secret = "your-secret-key-here"  # Should be in settings
        expected_signature = hmac.new(secret.encode(), token_data.encode(), hashlib.sha256).hexdigest()
        
        if signature != expected_signature:
            return None
            
        payload = json.loads(token_data)
        
        # Check expiration
        import time
        if payload['exp'] < time.time():
            return None
            
        return payload
    except Exception:
        return None


@csrf_exempt
@require_http_methods(["POST"])
def token_obtain_pair(request):
    """
    Custom token obtain view
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'error': 'Username and password are required'
            }, status=400)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is None:
            return JsonResponse({
                'detail': 'No active account found with the given credentials'
            }, status=401)
        
        if not user.is_active:
            return JsonResponse({
                'detail': 'User account is disabled'
            }, status=401)
        
        # Create tokens
        access_token = create_token(user.id, user.username)
        ***REMOVED***= create_token(user.id, user.username)  # Simplified - same for now
        
        return JsonResponse({
            'access': access_token,
            'refresh': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Internal server error',
            'detail': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def token_refresh(request):
    """
    Custom token refresh view
    """
    try:
        data = json.loads(request.body)
        ***REMOVED***= data.get('refresh')
        
        if not refresh_token:
            return JsonResponse({
                'error': 'Refresh token is required'
            }, status=400)
        
        # Verify refresh token
        payload = verify_token(refresh_token)
        if not payload:
            return JsonResponse({
                'detail': 'Token is invalid or expired'
            }, status=401)
        
        # Create new access token
        access_token = create_token(payload['user_id'], payload['username'])
        
        return JsonResponse({
            'access': access_token
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Internal server error',
            'detail': str(e)
        }, status=500)


def test_credentials(request):
    """Test endpoint to validate existing credentials"""
    return JsonResponse({
        'message': 'Test endpoint for credential validation',
        'available_users': [
            {'username': 'admin', 'note': 'superuser'},
            {'username': 'timberpups', 'note': 'regular user'}
        ],
        'instructions': 'Use POST /api/token/ with username and password to get tokens'
    })