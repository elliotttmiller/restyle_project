#!/usr/bin/env python3
"""
Simple eBay Setup Test
Checks current eBay configuration and provides setup instructions
"""

import os
import sys
import requests
import json
from datetime import datetime

def check_current_setup():
    """Check the current eBay setup status"""
    print("🔍 CHECKING CURRENT EBAY SETUP")
    print("=" * 40)
    
    # Check if we can access the backend settings
    try:
        # Try to import Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.backend.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        
        # Check eBay credentials
        app_id = getattr(settings, 'EBAY_PRODUCTION_APP_ID', None)
        cert_id = getattr(settings, 'EBAY_PRODUCTION_CERT_ID', None)
        client_secret = getattr(settings, 'EBAY_PRODUCTION_CLIENT_SECRET', None)
        refresh_token = getattr(settings, 'EBAY_PRODUCTION_REFRESH_TOKEN', None)
        
        print("📋 CURRENT EBAY CREDENTIALS:")
        print(f"   App ID: {'✅ Set' if app_id and app_id != 'Your-App-ID-Goes-Here' else '❌ Placeholder'}")
        print(f"   Cert ID: {'✅ Set' if cert_id and cert_id != 'Your-Cert-ID-Goes-Here' else '❌ Placeholder'}")
        print(f"   Client Secret: {'✅ Set' if client_secret and client_secret != 'Your-Client-Secret-Goes-Here' else '❌ Placeholder'}")
        print(f"   Refresh Token: {'✅ Set' if refresh_token else '❌ Missing'}")
        
        return app_id, cert_id, client_secret, refresh_token
        
    except Exception as e:
        print(f"❌ Error accessing Django settings: {e}")
        return None, None, None, None

def test_ai_system_response():
    """Test the AI system response to see if it's working"""
    print("\n🤖 TESTING AI SYSTEM RESPONSE")
    print("=" * 35)
    
    try:
        # Use the test image
        test_image_path = r"C:\Users\AMD\restyle_project\test_files\example.JPG"
        
        if not os.path.exists(test_image_path):
            print(f"❌ Test image not found: {test_image_path}")
            return False
        
        # Prepare the request
        url = "http://localhost:8000/api/core/ai/advanced-search/"
        
        with open(test_image_path, 'rb') as f:
            files = {'image': ('test.jpg', f, 'image/jpeg')}
            data = {'image_type': 'image/jpeg'}
            
            print("Sending image to AI system...")
            response = requests.post(url, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI system is working!")
            
            # Check what we got back
            search_results = result.get('search_results', [])
            query_variants = result.get('query_variants', [])
            confidence_scores = result.get('confidence_scores', {})
            
            print(f"\n📊 RESPONSE ANALYSIS:")
            print(f"   Search Results: {len(search_results)} items")
            print(f"   Query Variants: {len(query_variants)} options")
            print(f"   AI Services: {len(confidence_scores)} active")
            
            if search_results:
                print("\n📦 EBAY LISTINGS FOUND:")
                for i, item in enumerate(search_results[:3], 1):
                    title = item.get('title', 'No title')
                    price = item.get('price', 'No price')
                    print(f"   {i}. {title} - {price}")
                return True
            else:
                print("\n⚠️  NO EBAY LISTINGS FOUND")
                print("   This means eBay credentials need to be configured")
                return False
        else:
            print(f"❌ AI system request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI system: {e}")
        return False

def provide_setup_instructions():
    """Provide clear setup instructions"""
    print("\n📝 EBAY SETUP INSTRUCTIONS")
    print("=" * 35)
    print("To get real eBay listings, you need to:")
    print()
    print("1. 🌐 Go to eBay Developer Program")
    print("   https://developer.ebay.com/")
    print()
    print("2. 📝 Create a Developer Account")
    print("   - Sign up for free")
    print("   - Create a new application")
    print()
    print("3. 🔑 Get Your Credentials")
    print("   You'll need these from your eBay app:")
    print("   - App ID (Client ID)")
    print("   - Cert ID (Client Secret)")
    print("   - Client Secret")
    print("   - Refresh Token (from OAuth flow)")
    print()
    print("4. ⚙️  Update Configuration")
    print("   Edit: backend/backend/local_settings.py")
    print("   Replace the placeholder values with your real credentials")
    print()
    print("5. 🔄 Restart Backend")
    print("   docker compose restart backend")
    print()
    print("6. ✅ Test Again")
    print("   python test_files/test_ebay_setup_simple.py")

def main():
    """Main test function"""
    print("🚀 EBAY SETUP TEST")
    print("=" * 30)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Check current setup
    app_id, cert_id, client_secret, refresh_token = check_current_setup()
    
    # Test AI system
    ai_working = test_ai_system_response()
    
    # Check if we have real credentials
    has_real_creds = all([
        app_id and app_id != 'Your-App-ID-Goes-Here',
        cert_id and cert_id != 'Your-Cert-ID-Goes-Here',
        client_secret and client_secret != 'Your-Client-Secret-Goes-Here',
        refresh_token
    ])
    
    print("\n📊 SUMMARY")
    print("=" * 15)
    print(f"AI System: {'✅ Working' if ai_working else '❌ Failed'}")
    print(f"eBay Credentials: {'✅ Configured' if has_real_creds else '❌ Need Setup'}")
    
    if has_real_creds and ai_working:
        print("\n🎉 EBAY INTEGRATION READY!")
        print("   Real eBay listings should appear in the mobile app!")
    else:
        print("\n⚠️  EBAY SETUP NEEDED")
        provide_setup_instructions()

if __name__ == "__main__":
    main() 