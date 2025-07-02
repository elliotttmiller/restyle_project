#!/usr/bin/env python3
"""
Test Auth'n'Auth eBay search functionality
"""

import requests
import json

def test_authn_auth_search():
    """Test the eBay search with Auth'n'Auth token"""
    print("Testing Auth'n'Auth eBay Search")
    print("=" * 50)
    
    # Test the search endpoint
    try:
        response = requests.get(
            "http://localhost:8000/api/core/ebay-search/",
            params={"q": "nike shoes"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful! Found {len(data)} items")
            
            if data:
                print("\nSample item:")
                item = data[0]
                print(f"  Title: {item.get('title', 'N/A')[:50]}...")
                print(f"  Price: ${item.get('price', {}).get('value', 'N/A')}")
                print(f"  Condition: {item.get('condition', [{}])[0].get('conditionDisplayName', 'N/A')}")
                print(f"  URL: {item.get('itemWebUrl', 'N/A')}")
            
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        print("Make sure the backend is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_authn_auth_search() 