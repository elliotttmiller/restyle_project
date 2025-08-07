#!/usr/bin/env python3
"""
eBay Configuration Test Script
Tests the current eBay setup and helps configure real eBay listings
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the backend to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_ebay_credentials():
    """Test if eBay credentials are properly configured"""
    print("🔍 TESTING EBAY CONFIGURATION")
    print("=" * 50)
    
    try:
        from django.conf import settings
        
        # Check if credentials are set
        app_id = getattr(settings, 'EBAY_PRODUCTION_APP_ID', None)
        cert_id = getattr(settings, 'EBAY_PRODUCTION_CERT_ID', None)
        ***REMOVED*** = getattr(settings, 'EBAY_PRODUCTION_CLIENT_SECRET', None)
        ***REMOVED***= getattr(settings, 'EBAY_PRODUCTION_REFRESH_TOKEN', None)
        
        print("📋 CREDENTIAL STATUS:")
        print(f"   App ID: {'✅ Set' if app_id and app_id != 'Your-App-ID-Goes-Here' else '❌ Missing/Placeholder'}")
        print(f"   Cert ID: {'✅ Set' if cert_id and cert_id != 'Your-Cert-ID-Goes-Here' else '❌ Missing/Placeholder'}")
        print(f"   Client Secret: {'✅ Set' if ***REMOVED*** and ***REMOVED*** != 'Your-Client-Secret-Goes-Here' else '❌ Missing/Placeholder'}")
        print(f"   Refresh Token: {'✅ Set' if ***REMOVED***else '❌ Missing'}")
        
        # Check if all credentials are properly set
        all_set = all([
            app_id and app_id != 'Your-App-ID-Goes-Here',
            cert_id and cert_id != 'Your-Cert-ID-Goes-Here', 
            ***REMOVED*** and ***REMOVED*** != 'Your-Client-Secret-Goes-Here',
            refresh_token
        ])
        
        if all_set:
            print("\n✅ All eBay credentials are properly configured!")
            return True
        else:
            print("\n❌ eBay credentials need to be configured for real listings.")
            print("\n📝 NEXT STEPS:")
            print("1. Get eBay Developer credentials from https://developer.ebay.com/")
            print("2. Update backend/backend/local_settings.py with your credentials")
            print("3. Restart the backend: docker compose restart backend")
            print("4. Run this test again")
            return False
            
    except Exception as e:
        print(f"❌ Error testing eBay configuration: {e}")
        return False

def test_ebay_token():
    """Test if we can get a valid eBay OAuth token"""
    print("\n🔑 TESTING EBAY TOKEN")
    print("=" * 30)
    
    try:
        from backend.core.ebay_auth import get_ebay_oauth_token
        
        token = get_ebay_oauth_token()
        if token:
            print("✅ eBay OAuth token obtained successfully!")
            print(f"   Token: {token[:20]}...{token[-20:]}")
            return True
        else:
            print("❌ Failed to get eBay OAuth token")
            return False
            
    except Exception as e:
        print(f"❌ Error getting eBay token: {e}")
        return False

def test_ebay_search():
    """Test if we can search eBay for real listings"""
    print("\n🔍 TESTING EBAY SEARCH")
    print("=" * 30)
    
    try:
        from backend.core.services import EbayService
        
        # Create eBay service
        ebay_service = EbayService()
        
        # Test search
        print("Searching for 'shirt' on eBay...")
        results = ebay_service.search_items('shirt', limit=3)
        
        if results:
            print(f"✅ Found {len(results)} real eBay listings!")
            print("\n📦 SAMPLE LISTINGS:")
            for i, item in enumerate(results[:3], 1):
                title = item.get('title', 'No title')
                price = item.get('price', {}).get('value', 'No price')
                currency = item.get('price', {}).get('currency', '')
                url = item.get('itemWebUrl', 'No URL')
                
                print(f"   {i}. {title}")
                print(f"      Price: {price} {currency}")
                print(f"      URL: {url}")
                print()
            return True
        else:
            print("❌ No eBay search results found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing eBay search: {e}")
        return False

def test_ai_system_with_ebay():
    """Test the full AI system with eBay integration"""
    print("\n🤖 TESTING AI SYSTEM WITH EBAY")
    print("=" * 40)
    
    try:
        import requests
        from PIL import Image
        import io
        
        # Use the test image
        test_image_path = r"C:\Users\AMD\restyle_project\test_files\example.JPG"
        
        if not os.path.exists(test_image_path):
            print(f"❌ Test image not found: {test_image_path}")
            return False
        
        # Prepare the request
        url = "https://restyleproject-production.up.railway.app/api/core/ai/advanced-search/"
        
        with open(test_image_path, 'rb') as f:
            files = {'image': ('test.jpg', f, 'image/jpeg')}
            data = {'image_type': 'image/jpeg'}
            
            print("Sending image to AI system with eBay search...")
            response = requests.post(url, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI system with eBay search successful!")
            
            # Check for eBay results
            search_results = result.get('search_results', [])
            if search_results:
                print(f"📦 Found {len(search_results)} eBay listings!")
                print("\n🎯 AI-GENERATED QUERIES:")
                queries = result.get('query_variants', [])
                for i, query in enumerate(queries[:3], 1):
                    print(f"   {i}. {query.get('query', 'No query')} ({query.get('confidence', 0)}%)")
                
                print("\n📊 EBAY LISTINGS:")
                for i, item in enumerate(search_results[:3], 1):
                    title = item.get('title', 'No title')
                    price = item.get('price', 'No price')
                    print(f"   {i}. {title} - {price}")
                
                return True
            else:
                print("⚠️  AI system working but no eBay results found")
                print("   This could be due to:")
                print("   - eBay credentials not configured")
                print("   - Search query not finding matches")
                print("   - Rate limiting")
                return False
        else:
            print(f"❌ AI system request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI system with eBay: {e}")
        return False

def main():
    """Run all eBay configuration tests"""
    print("🚀 EBAY CONFIGURATION TEST SUITE")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Test 1: Check credentials
    creds_ok = test_ebay_credentials()
    
    # Test 2: Check token (only if credentials are set)
    token_ok = False
    if creds_ok:
        token_ok = test_ebay_token()
    
    # Test 3: Check search (only if token is working)
    search_ok = False
    if token_ok:
        search_ok = test_ebay_search()
    
    # Test 4: Check full AI system
    ai_ok = test_ai_system_with_ebay()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 20)
    print(f"Credentials: {'✅ OK' if creds_ok else '❌ NEEDS SETUP'}")
    print(f"Token: {'✅ OK' if token_ok else '❌ FAILED'}")
    print(f"Search: {'✅ OK' if search_ok else '❌ FAILED'}")
    print(f"AI System: {'✅ OK' if ai_ok else '❌ FAILED'}")
    
    if all([creds_ok, token_ok, search_ok, ai_ok]):
        print("\n🎉 EBAY INTEGRATION FULLY WORKING!")
        print("   Real eBay listings will appear in the mobile app!")
    else:
        print("\n⚠️  EBAY INTEGRATION NEEDS CONFIGURATION")
        print("   Follow the setup guide in EBAY_SETUP_GUIDE.md")

if __name__ == "__main__":
    main() 