#!/usr/bin/env python3
"""
Test automated token refresh integration
"""

import os
import sys
import requests
import json
import traceback

# Add the backend directory to the Python path
print(f'[DEBUG] Before sys.path.insert, os: {os}')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
print(f'[DEBUG] After sys.path.insert, os: {os}')

def test_token_refresh_integration():
    import os
    print(f"os module (inside function): {os}")
    print("🔍 TESTING AUTOMATED TOKEN REFRESH INTEGRATION")
    print("=" * 50)
    
    try:
        # Set up Django
        print(f'[DEBUG] Before os.environ, os: {os}')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        print(f'[DEBUG] After os.environ, os: {os}')
        
        import django
        django.setup()
        
        from django.conf import settings
        from core.ebay_auth import token_manager, get_ebay_oauth_token
        from core.services import EbayService
        
        print("📋 CHECKING EBAY CREDENTIALS:")
        print(f"   App ID: {getattr(settings, 'EBAY_PRODUCTION_APP_ID', 'Not set')}")
        print(f"   Cert ID: {getattr(settings, 'EBAY_PRODUCTION_CERT_ID', 'Not set')}")
        print(f"   Client Secret: {getattr(settings, 'EBAY_PRODUCTION_CLIENT_SECRET', 'Not set')}")
        print(f"   Refresh Token: {getattr(settings, 'EBAY_PRODUCTION_REFRESH_TOKEN', 'Not set')[:50]}...")
        
        print("\n🔑 TESTING TOKEN MANAGER:")
        
        # Test token manager directly
        try:
            print("   Testing token manager get_valid_token()...")
            token1 = token_manager.get_valid_token()
            if token1:
                print(f"   ✅ Token manager returned token: {token1[:50]}...")
            else:
                print("   ❌ Token manager returned no token")
        except Exception as e:
            print(f"   ❌ Token manager error: {e}")
        
        # Test the get_ebay_oauth_token function
        try:
            print("   Testing get_ebay_oauth_token() function...")
            token2 = get_ebay_oauth_token()
            if token2:
                print(f"   ✅ Function returned token: {token2[:50]}...")
            else:
                print("   ❌ Function returned no token")
        except Exception as e:
            print(f"   ❌ Function error: {e}")
        
        # Test EbayService integration
        try:
            print("\n🔧 TESTING EBAY SERVICE INTEGRATION:")
            ebay_service = EbayService()
            if ebay_service.auth_token:
                print(f"   ✅ EbayService has token: {ebay_service.auth_token[:50]}...")
                
                # Test a simple search
                print("   Testing eBay search with service...")
                results = ebay_service.search_items("test", limit=1)
                print(f"   ✅ Search returned {len(results)} results")
                
                if results:
                    print("   📦 Sample result:")
                    item = results[0]
                    print(f"      Title: {item.get('title', 'No title')}")
                    print(f"      Price: {item.get('price', 'No price')}")
                else:
                    print("   ⚠️  No search results returned")
            else:
                print("   ❌ EbayService has no token")
        except Exception as e:
            print(f"   ❌ EbayService error: {e}")
        
        # Test token validation
        if token1:
            print("\n🔍 TESTING TOKEN VALIDATION:")
            try:
                is_valid = token_manager.validate_token(token1)
                if is_valid:
                    print("   ✅ Token is valid!")
                else:
                    print("   ❌ Token is invalid")
            except Exception as e:
                print(f"   ❌ Token validation error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing token refresh integration: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_token_refresh_integration() 