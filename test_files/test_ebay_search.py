#!/usr/bin/env python3
"""
Test script for eBay search functionality
"""

import requests
import json
import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.conf import settings

def test_ebay_search():
    """Test the eBay search functionality"""
    print("Testing eBay Search Functionality")
    print("=" * 50)
    
    # Test 1: Check if eBay credentials are configured
    print("\n1. Checking eBay credentials...")
    oauth_token = getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None)
    if oauth_token:
        print("✅ eBay OAuth token is configured")
        print(f"   Token length: {len(oauth_token)} characters")
    else:
        print("❌ eBay OAuth token is not configured")
        return False
    
    # Test 2: Test direct eBay API call
    print("\n2. Testing direct eBay API call...")
    try:
        api_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        params = {
            "q": "nike shoes",
            "limit": 5
        }
        headers = {
            "Authorization": f"Bearer {oauth_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.get(api_url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('itemSummaries', [])
            print(f"✅ eBay API call successful - found {len(items)} items")
            
            if items:
                print("   Sample item:")
                item = items[0]
                print(f"   - Title: {item.get('title', 'N/A')[:50]}...")
                print(f"   - Price: ${item.get('price', {}).get('value', 'N/A')}")
                print(f"   - Condition: {item.get('condition', 'N/A')}")
        else:
            print(f"❌ eBay API call failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error testing eBay API: {e}")
        return False
    
    # Test 3: Test our backend endpoint (requires authentication)
    print("\n3. Testing backend endpoint...")
    print("   Note: This requires authentication - you'll need to test via the frontend")
    print("   The endpoint is available at: http://localhost:8000/api/core/ebay-search/")
    
    return True

def test_backend_health():
    """Test if the backend is running"""
    print("\n4. Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/api/core/health/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend is not running: {e}")
        return False

if __name__ == "__main__":
    print("eBay Search Test Suite")
    print("=" * 50)
    
    # Test backend health first
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start it with:")
        print("   cd backend && python manage.py runserver 8000")
        sys.exit(1)
    
    # Test eBay search functionality
    if test_ebay_search():
        print("\n✅ All tests passed!")
        print("\nNext steps:")
        print("1. Make sure the frontend is running: cd frontend && npm start")
        print("2. Open http://localhost:3000 in your browser")
        print("3. Log in and test the search functionality on the dashboard")
    else:
        print("\n❌ Some tests failed. Check the configuration.")
        sys.exit(1) 