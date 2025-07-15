#!/usr/bin/env python3
"""
Test JWT token refresh integration
"""

import os
import sys
import requests
import json

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_jwt_refresh_integration():
    """Test if JWT token refresh is working"""
    print("🔍 TESTING JWT TOKEN REFRESH INTEGRATION")
    print("=" * 50)
    
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        
        import django
        django.setup()
        
        from django.contrib.auth import get_user_model
        from django.conf import settings
        
        User = get_user_model()
        
        # Test data
        test_username = "testuser"
        test_password = "testpass123"
        
        # Create a test user if it doesn't exist
        try:
            user = User.objects.get(username=test_username)
            print(f"✅ Using existing test user: {test_username}")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=test_username,
                password=test_password,
                email="test@example.com"
            )
            print(f"✅ Created test user: {test_username}")
        
        # Test JWT token endpoints
        base_url = "http://localhost:8000/api"
        
        print("\n🔑 TESTING JWT TOKEN ENDPOINTS:")
        
        # 1. Test token obtain (login)
        print("   Testing token obtain...")
        login_response = requests.post(f"{base_url}/token/", {
            "username": test_username,
            "password": test_password
        })
        
        if login_response.status_code == 200:
            tokens = login_response.json()
            access_token = tokens.get('access')
            ***REMOVED***= tokens.get('refresh')
            
            print(f"   ✅ Login successful")
            print(f"   Access token: {access_token[:50]}...")
            print(f"   Refresh token: {refresh_token[:50]}...")
            
            # 2. Test token refresh
            print("\n   Testing token refresh...")
            refresh_response = requests.post(f"{base_url}/token/refresh/", {
                "refresh": refresh_token
            })
            
            if refresh_response.status_code == 200:
                new_tokens = refresh_response.json()
                new_access_token = new_tokens.get('access')
                
                print(f"   ✅ Token refresh successful")
                print(f"   New access token: {new_access_token[:50]}...")
                
                # 3. Test that the new token works
                print("\n   Testing new token...")
                headers = {"Authorization": f"Bearer {new_access_token}"}
                test_response = requests.get(f"{base_url}/core/health-check/", headers=headers)
                
                if test_response.status_code == 200:
                    print(f"   ✅ New token works correctly")
                else:
                    print(f"   ❌ New token failed: {test_response.status_code}")
                
            else:
                print(f"   ❌ Token refresh failed: {refresh_response.status_code}")
                print(f"   Response: {refresh_response.text}")
                
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing JWT refresh integration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_jwt_refresh_integration() 