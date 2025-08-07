#!/usr/bin/env python3
"""
Quick eBay validation test
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.ebay_auth import token_manager
from core.services import EbayService

def test_ebay_quick():
    """Quick eBay functionality test"""
    print("🚀 Quick eBay Validation Test")
    print("=" * 50)
    
    # Test 1: Token management
    print("\n1. Testing Token Management:")
    try:
        # Test get_access_token method (new alias)
        token = token_manager.get_access_token()
        print(f"   ✅ get_access_token(): {'Found' if token else 'None'}")
        
        # Test is_token_valid method (new method)
        is_valid = token_manager.is_token_valid()
        print(f"   ✅ is_token_valid(): {is_valid}")
        
        # Test original get_valid_token method
        valid_token = token_manager.get_valid_token()
        print(f"   ✅ get_valid_token(): {'Found' if valid_token else 'None'}")
        
    except Exception as e:
        print(f"   ❌ Token management error: {e}")
    
    # Test 2: eBay Service
    print("\n2. Testing eBay Service:")
    try:
        ebay_service = EbayService()
        print(f"   ✅ EbayService initialized: {ebay_service is not None}")
        print(f"   ✅ Has auth token: {ebay_service.auth_token is not None}")
        
        # Test search with a simple query
        results = ebay_service.search_items("test", limit=1)
        print(f"   ✅ Search test: {'Success' if results is not None else 'Failed'}")
        print(f"   ✅ Results count: {len(results) if results else 0}")
        
    except Exception as e:
        print(f"   ❌ eBay service error: {e}")
    
    # Test 3: Credential validation
    print("\n3. Testing Credential Status:")
    try:
        from core.credential_manager import credential_manager
        status = credential_manager.get_service_status()
        ebay_status = status.get('ebay_api', {})
        print(f"   ✅ eBay enabled: {ebay_status.get('enabled', False)}")
        print(f"   ✅ eBay available: {ebay_status.get('available', False)}")
        print(f"   ✅ eBay credentials: {ebay_status.get('credentials', False)}")
        
    except Exception as e:
        print(f"   ❌ Credential status error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Quick validation test completed!")

if __name__ == "__main__":
    test_ebay_quick()
