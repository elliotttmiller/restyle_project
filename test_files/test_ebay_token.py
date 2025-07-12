#!/usr/bin/env python3
"""
Test eBay token functionality
"""

import os
import sys
import requests
import json

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_ebay_token():
    """Test if eBay token is working"""
    print("🔍 TESTING EBAY TOKEN")
    print("=" * 30)
    
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.backend.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        from core.ebay_auth import get_ebay_oauth_token, token_manager
        
        print("📋 CHECKING EBAY CREDENTIALS:")
        print(f"   App ID: {getattr(settings, 'EBAY_PRODUCTION_APP_ID', 'Not set')}")
        print(f"   Cert ID: {getattr(settings, 'EBAY_PRODUCTION_CERT_ID', 'Not set')}")
        print(f"   Client Secret: {getattr(settings, 'EBAY_PRODUCTION_CLIENT_SECRET', 'Not set')}")
        print(f"   Refresh Token: {getattr(settings, 'EBAY_PRODUCTION_REFRESH_TOKEN', 'Not set')[:50]}...")
        
        print("\n🔑 TESTING TOKEN RETRIEVAL:")
        
        # Test token manager
        try:
            print("   Using token manager...")
            token = token_manager.get_valid_token()
            if token:
                print(f"   ✅ Token obtained: {token[:50]}...")
            else:
                print("   ❌ Token manager failed to get token")
        except Exception as e:
            print(f"   ❌ Token manager error: {e}")
            token = None
        
        # Test direct token function
        try:
            print("   Testing direct token function...")
            direct_token = get_ebay_oauth_token()
            if direct_token:
                print(f"   ✅ Direct token: {direct_token[:50]}...")
            else:
                print("   ❌ Direct token function failed")
        except Exception as e:
            print(f"   ❌ Direct token function error: {e}")
            direct_token = None
        
        # Test token validation
        if token:
            print("\n🔍 TESTING TOKEN VALIDATION:")
            test_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'X-EBAY-C-MARKETPLACE-ID': 'EBAY-US'
            }
            params = {'q': 'test', 'limit': 1}
            
            response = requests.get(test_url, headers=headers, params=params, timeout=10)
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Token is valid!")
                data = response.json()
                print(f"   Found {len(data.get('itemSummaries', []))} test items")
            else:
                print(f"   ❌ Token validation failed: {response.text[:200]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing eBay token: {e}")
        return False

if __name__ == "__main__":
    test_ebay_token() 