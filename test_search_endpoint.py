#!/usr/bin/env python3
"""
Test script to verify the backend search endpoint is working with the new token
"""

import requests
import json

def test_search_endpoint():
    """Test the backend search endpoint"""
    print("🧪 Testing Backend Search Endpoint")
    print("=" * 50)
    
    # Test the search endpoint
    url = "http://localhost:8000/api/core/ebay-search/"
    params = {
        'q': 'Nike shoes',
        'limit': 5
    }
    
    try:
        print(f"🔍 Making request to: {url}")
        print(f"📋 Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Search endpoint successful!")
            print(f"📦 Found {len(data.get('itemSummaries', []))} items")
            
            # Show first item details
            items = data.get('itemSummaries', [])
            if items:
                first_item = items[0]
                print(f"\n📦 First item:")
                print(f"   Title: {first_item.get('title', 'N/A')}")
                print(f"   Price: ${first_item.get('price', {}).get('value', 'N/A')}")
                print(f"   URL: {first_item.get('itemWebUrl', 'N/A')}")
            
            return True
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Error during search test: {e}")
        return False

if __name__ == "__main__":
    success = test_search_endpoint()
    if success:
        print("\n🎉 Search endpoint test successful! The application is working with the new token.")
    else:
        print("\n💥 Search endpoint test failed. Please check the backend configuration.") 