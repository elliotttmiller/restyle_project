#!/usr/bin/env python3
"""
Simple JWT token refresh test via HTTP requests
"""

import requests
import json

def test_jwt_refresh_simple():
    print("🔍 TESTING JWT TOKEN REFRESH (HTTP)")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    
    try:
        test_username = "admin"
        test_password = "elliott123"
        print(f"🔑 Testing with user: {test_username}")
        
        print("[DEBUG] About to POST /token/")
        login_response = requests.post(f"{base_url}/token/", {
            "username": test_username,
            "password": test_password
        })
        print(f"[DEBUG] /token/ response: {login_response.status_code}")
        
        if login_response.status_code == 200:
            tokens = login_response.json()
            access_token = tokens.get('access')
            ***REMOVED***= tokens.get('refresh')
            print(f"   ✅ Login successful")
            print(f"   Access token: {access_token[:50]}...")
            print(f"   Refresh token: {refresh_token[:50]}...")
            
            print("[DEBUG] About to POST /token/refresh/")
            refresh_response = requests.post(f"{base_url}/token/refresh/", {
                "refresh": refresh_token
            })
            print(f"[DEBUG] /token/refresh/ response: {refresh_response.status_code}")
            
            if refresh_response.status_code == 200:
                new_tokens = refresh_response.json()
                new_access_token = new_tokens.get('access')
                print(f"   ✅ Token refresh successful")
                print(f"   New access token: {new_access_token[:50]}...")
                
                print("[DEBUG] About to GET /core/health-check/")
                headers = {"Authorization": f"Bearer {new_access_token}"}
                test_response = requests.get(f"{base_url}/core/health-check/", headers=headers)
                print(f"[DEBUG] /core/health-check/ response: {test_response.status_code}")
                
                if test_response.status_code == 200:
                    print(f"   ✅ New token works correctly")
                    print(f"   Response: {test_response.json()}")
                else:
                    print(f"   ❌ New token failed: {test_response.status_code}")
                    print(f"   Response: {test_response.text}")
            else:
                print(f"   ❌ Token refresh failed: {refresh_response.status_code}")
                print(f"   Response: {refresh_response.text}")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            print(f"\n💡 TIP: Make sure you have a user with username '{test_username}' and password '{test_password}'")
            print(f"   You can create one via Django admin or change the credentials in this test.")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure the backend is running:")
        print("   docker compose up backend")
        return False
    except Exception as e:
        print(f"❌ Error testing JWT refresh: {e}")
        return False

if __name__ == "__main__":
    test_jwt_refresh_simple() 