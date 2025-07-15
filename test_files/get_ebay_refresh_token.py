#!/usr/bin/env python3
"""
eBay OAuth Refresh Token Helper
Helps you get a refresh token for eBay API access
"""

import webbrowser
import requests
import json
from datetime import datetime

def main():
    """Guide user through eBay OAuth process"""
    print("🔑 EBAY OAUTH REFRESH TOKEN HELPER")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    print("📋 PREREQUISITES:")
    print("1. You need your eBay App ID, Cert ID, and Client Secret")
    print("2. Your eBay app must be configured with the correct URLs")
    print("3. Ngrok must be running")
    print()
    
    print("🌐 STEP 1: Configure eBay App URLs")
    print("In your eBay Developer Console, set these URLs:")
    print()
    print("Privacy Policy URL:")
    print("https://ead6946c7030.ngrok-free.app/api/core/privacy-policy/")
    print()
    print("Auth Accepted URL:")
    print("https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth-callback/")
    print()
    print("Auth Declined URL:")
    print("https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth-declined/")
    print()
    
    print("🔑 STEP 2: Get Your Credentials")
    print("From your eBay app, you need:")
    print("- App ID (Client ID)")
    print("- Cert ID (Client Secret)")
    print("- Client Secret")
    print()
    
    # Ask for credentials
    app_id = input("Enter your eBay App ID: ").strip()
    cert_id = input("Enter your eBay Cert ID: ").strip()
    ***REMOVED*** = input("Enter your eBay Client Secret: ").strip()
    
    if not all([app_id, cert_id, ***REMOVED***]):
        print("❌ All credentials are required!")
        return
    
    print()
    print("✅ Credentials received!")
    print()
    
    print("🌐 STEP 3: Start OAuth Flow")
    print("Opening OAuth URL in browser...")
    
    # Open the OAuth URL
    oauth_url = "https://ead6946c7030.ngrok-free.app/api/core/ebay-oauth/"
    print(f"OAuth URL: {oauth_url}")
    
    try:
        webbrowser.open(oauth_url)
        print("✅ Browser opened! Complete the OAuth flow.")
        print()
        print("📝 STEP 4: Complete OAuth Flow")
        print("1. Sign in with your eBay account")
        print("2. Grant permissions to your app")
        print("3. You'll be redirected back with a refresh token")
        print()
        print("🔄 STEP 5: Update Settings")
        print("Once you have the refresh token, update:")
        print("backend/backend/local_settings.py")
        print()
        print("With your credentials:")
        print(f"EBAY_PRODUCTION_APP_ID = '{app_id}'")
        print(f"EBAY_PRODUCTION_CERT_ID = '{cert_id}'")
        print(f"EBAY_PRODUCTION_CLIENT_SECRET = '{***REMOVED***}'")
        print("EBAY_PRODUCTION_REFRESH_TOKEN = 'your-refresh-token'")
        print()
        print("🔄 STEP 6: Restart and Test")
        print("docker compose restart backend")
        print("python test_files/test_ebay_setup_simple.py")
        
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"Please manually visit: {oauth_url}")

if __name__ == "__main__":
    main() 