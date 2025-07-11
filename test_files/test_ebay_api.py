#!/usr/bin/env python3
"""
Test script to debug eBay API connection
"""

import os
import sys
import django
import requests
import json

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

def test_ebay_api():
    print("🧪 Testing eBay API Connection...")
    
    # Check settings
    use_sandbox = getattr(settings, 'EBAY_SANDBOX', False)
    print(f"Using Sandbox: {use_sandbox}")
    
    if use_sandbox:
        app_id = getattr(settings, 'EBAY_SANDBOX_APP_ID', None)
        api_url = "https://svcs.sandbox.ebay.com/services/search/FindingService/v1"
    else:
        app_id = getattr(settings, 'EBAY_PRODUCTION_APP_ID', None)
        api_url = "https://svcs.ebay.com/services/search/FindingService/v1"
    
    print(f"App ID: {app_id}")
    print(f"API URL: {api_url}")
    
    if not app_id:
        print("❌ No App ID found!")
        return False
    
    # Test API call
    headers = {
        'X-EBAY-SOA-OPERATION-NAME': 'findCompletedItems',
        'X-EBAY-SOA-SECURITY-APPNAME': app_id,
        'X-EBAY-SOA-RESPONSE-DATA-FORMAT': 'JSON',
    }
    
    params = {
        'keywords': 'Levi jeans',
        'categoryId': '11450',
        'outputSelector': 'SellerInfo',
        'paginationInput.entriesPerPage': '5',
        'sortOrder': 'EndTimeSoonest',
    }
    
    print(f"\n🔍 Making API request...")
    print(f"URL: {api_url}")
    print(f"Headers: {headers}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API call successful!")
            print(f"Response data: {json.dumps(data, indent=2)[:1000]}...")
            
            # Check for items
            items = data.get('findCompletedItemsResponse', [{}])[0].get('searchResult', [{}])[0].get('item', [])
            print(f"Found {len(items)} items")
            
            if items:
                print("Sample item:")
                print(json.dumps(items[0], indent=2))
            else:
                print("No items found in response")
                
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error making API call: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_ebay_api() 