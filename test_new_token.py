#!/usr/bin/env python3
"""
Test script to verify the new eBay OAuth token is working
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

def test_new_token():
    """Test the new eBay OAuth token"""
    print("🧪 Testing New eBay OAuth Token")
    print("=" * 50)
    
    # Get the token from settings
    oauth_token = getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None)
    if not oauth_token:
        print("❌ No eBay OAuth token found in settings")
        return False
    
    print(f"✅ Found OAuth token (length: {len(oauth_token)} characters)")
    print(f"   Token starts with: {oauth_token[:20]}...")
    
    # Test eBay Browse API directly
    print("\n🔍 Testing eBay Browse API...")
    
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        'Authorization': f'Bearer {oauth_token}',
        'Content-Type': 'application/json',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY-US'
    }
    
    params = {
        'q': 'Nike shoes',
        'limit': 5
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('itemSummaries', [])
            print(f"✅ Success! Found {len(items)} items")
            
            # Show first item details
            if items:
                first_item = items[0]
                print(f"\n📦 First item:")
                print(f"   Title: {first_item.get('title', 'N/A')}")
                print(f"   Price: ${first_item.get('price', {}).get('value', 'N/A')}")
                print(f"   URL: {first_item.get('itemWebUrl', 'N/A')}")
            
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        return False

if __name__ == "__main__":
    success = test_new_token()
    if success:
        print("\n🎉 Token test successful! The new token is working.")
    else:
        print("\n💥 Token test failed. Please check the configuration.") 