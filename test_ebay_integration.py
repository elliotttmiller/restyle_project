#!/usr/bin/env python3
"""
Test script for eBay integration
Run this to verify that eBay API calls are working properly
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.tasks import get_ebay_oauth_token, call_ebay_browse_api
from core.models import Item, MarketAnalysis
from django.contrib.auth import get_user_model

def test_ebay_integration():
    print("🧪 Testing eBay Integration...")
    
    # Test 1: Check if we can get eBay OAuth token
    print("\n1. Testing eBay OAuth token...")
    token = get_ebay_oauth_token()
    if token:
        print(f"✅ OAuth token retrieved: {token[:20]}...")
    else:
        print("❌ Failed to get OAuth token")
        return False
    
    # Test 2: Check if we have any items in the database
    print("\n2. Checking database for items...")
    User = get_user_model()
    try:
        user = User.objects.first()
        if not user:
            print("❌ No users found in database")
            return False
        
        items = Item.objects.filter(owner=user)
        print(f"✅ Found {items.count()} items in database")
        
        if items.count() == 0:
            print("⚠️  No items found. Creating a test item...")
            test_item = Item.objects.create(
                owner=user,
                title="Test Item",
                brand="Test Brand",
                category="Test Category",
                size="M",
                color="Blue",
                condition="GUC"
            )
            print(f"✅ Created test item: {test_item.id}")
        else:
            test_item = items.first()
            print(f"✅ Using existing item: {test_item.title}")
        
        # Test 3: Create a market analysis
        print("\n3. Creating market analysis...")
        analysis, created = MarketAnalysis.objects.get_or_create(
            item=test_item,
            defaults={'status': 'PENDING'}
        )
        print(f"✅ Market analysis {'created' if created else 'found'}: {analysis.id}")
        
        # Test 4: Test eBay Browse API call
        print("\n4. Testing eBay Browse API...")
        result = call_ebay_browse_api(analysis.id)
        print(f"✅ eBay Browse API result: {result}")
        
        # Test 5: Check if comparable sales were created
        from core.models import ComparableSale
        comps = ComparableSale.objects.filter(analysis=analysis)
        print(f"✅ Found {comps.count()} comparable sales")
        
        if comps.count() > 0:
            print("📊 Sample comparable sale:")
            sample_comp = comps.first()
            print(f"   Title: {sample_comp.title}")
            print(f"   Price: ${sample_comp.sold_price}")
            print(f"   Platform: {sample_comp.platform}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ebay_integration()
    if success:
        print("\n🎉 All tests passed! eBay integration is working.")
    else:
        print("\n💥 Some tests failed. Check the errors above.")
        sys.exit(1) 