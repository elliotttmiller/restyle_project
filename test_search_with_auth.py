#!/usr/bin/env python3
"""
Test script to verify the backend search endpoint is working with authentication
"""

import requests
import json
import os

def test_search_with_auth():
    """Test the backend search endpoint with authentication"""
    print("🧪 Testing Backend Search Endpoint with Authentication")
    print("=" * 60)
    
    # First, let's try to authenticate
    auth_url = "http://localhost:8000/api/token/"
    
    # Try to use environment variables or default test credentials
    username = os.environ.get("DJANGO_TEST_USER", "testuser")
    password = os.environ.get("DJANGO_TEST_PASS", "testpass123")
    
    print(f"🔐 Attempting to authenticate as: {username}")
    
    auth_data = {
        'username': username,
        'password': password
    }
    
    try:
        # Try to authenticate
        auth_response = requests.post(auth_url, json=auth_data, timeout=10)
        print(f"📊 Auth response status: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            auth_result = auth_response.json()
            access_token = auth_result.get('access')
            if access_token:
                print("✅ Authentication successful!")
                
                # Now test the search endpoint with the token
                search_url = "http://localhost:8000/api/core/ebay-search/"
                params = {
                    'q': 'Nike shoes',
                    'limit': 5
                }
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                print(f"\n🔍 Testing search endpoint with token...")
                search_response = requests.get(search_url, params=params, headers=headers, timeout=30)
                print(f"📊 Search response status: {search_response.status_code}")
                
                if search_response.status_code == 200:
                    data = search_response.json()
                    print("✅ Search endpoint successful!")
                    print(f"📦 Found {len(data)} items")
                    
                    # Show first item details
                    if data:
                        first_item = data[0]
                        print(f"\n📦 First item:")
                        print(f"   Title: {first_item.get('title', 'N/A')}")
                        print(f"   Price: ${first_item.get('price', {}).get('value', 'N/A')}")
                        print(f"   URL: {first_item.get('itemWebUrl', 'N/A')}")
                    
                    return True
                else:
                    print(f"❌ Search failed: {search_response.status_code}")
                    print(f"📄 Response: {search_response.text}")
                    return False
            else:
                print("❌ No access token in auth response")
                return False
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print(f"📄 Response: {auth_response.text}")
            print("\n💡 You may need to create a test user first:")
            print("   python manage.py createsuperuser")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_search_with_auth()
    if success:
        print("\n🎉 Search test successful! The application is working with the new token.")
    else:
        print("\n💥 Search test failed. Please check the configuration.") 