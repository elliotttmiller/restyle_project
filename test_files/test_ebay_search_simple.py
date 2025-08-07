#!/usr/bin/env python3
"""
Simple test script to verify eBay search functionality
"""

import os
import sys
import django
import requests
import json
import getpass

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def get_jwt_token(username, password):
    """Obtain JWT token from Django backend"""
    url = "http://localhost:8000/api/token/"
    data = {"username": username, "password": password}
    try:
        resp = requests.post(url, json=data, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("access")
        else:
            print(f"❌ Failed to get JWT token: {resp.status_code} {resp.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting JWT token: {e}")
        return None

def test_ebay_search():
    """Test eBay search functionality"""
    print("Testing eBay search functionality...")
    
    # Check if we have the OAuth token
    token = getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None)
    if not token:
        print("❌ No eBay OAuth token found in settings")
        return False
    
    print(f"✅ Found OAuth token (length: {len(token)})")
    
    # Authenticate with Django backend
    username = os.environ.get("DJANGO_TEST_USER") or input("Django test username: ")
    password = os.environ.get("DJANGO_TEST_PASS") or getpass.getpass("Django test password: ")
    jwt_token = get_jwt_token(username, password)
    if not jwt_token:
        print("❌ Could not authenticate with Django backend.")
        return False
    print("✅ Authenticated with Django backend.")
    
    # Test the search endpoint
    try:
        # Test with a simple search query
        search_url = "http://localhost:8000/api/core/ebay-search/"
        search_data = {
            "q": "laptop",
            "limit": 5
        }
        headers = {"Authorization": f"Bearer {jwt_token}"}
        
        print(f"🔍 Testing search endpoint: {search_url}")
        print(f"📝 Search query: {search_data}")
        
        response = requests.post(search_url, json=search_data, headers=headers, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Search successful!")
            print(f"📦 Found {len(data.get('items', []))} items")
            
            # Show first item details
            if data.get('items'):
                first_item = data['items'][0]
                print(f"📋 First item: {first_item.get('title', 'No title')}")
                print(f"💰 Price: {first_item.get('price', 'No price')}")
                print(f"🔗 URL: {first_item.get('itemWebUrl', 'No URL')}")
            
            return True
        else:
            print(f"❌ Search failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        print("💡 Make sure the Django backend is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error during search test: {e}")
        return False

def test_ebay_api_direct():
    """Test eBay API directly"""
    print("\nTesting eBay API directly...")
    
    token = getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None)
    if not token:
        print("❌ No eBay OAuth token found")
        return False
    
    try:
        # Test eBay Browse API directly
        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY-US'
        }
        
        params = {
            'q': 'laptop',
            'limit': 3
        }
        
        print(f"🔍 Testing eBay Browse API directly...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Direct API call successful!")
            print(f"📦 Found {len(data.get('itemSummaries', []))} items")
            return True
        else:
            print(f"❌ Direct API call failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during direct API test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting eBay search tests...\n")
    
    # Test 1: Direct API call
    direct_success = test_ebay_api_direct()
    
    # Test 2: Backend endpoint
    backend_success = test_ebay_search()
    
    print("\n" + "="*50)
    print("📊 Test Results Summary:")
    print(f"🔗 Direct API: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"🌐 Backend Endpoint: {'✅ PASS' if backend_success else '❌ FAIL'}")
    
    if direct_success and backend_success:
        print("\n🎉 All tests passed! eBay search is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.") 