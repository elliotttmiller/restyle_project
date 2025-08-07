#!/usr/bin/env python3
"""
Debug script to check what credentials are actually loaded
"""
import os
import sys
import django
from dotenv import load_dotenv

# Load .env file from project root
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.credential_manager import credential_manager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def debug_credentials():
    """Debug credential loading"""
    print("🔍 Debug Credential Loading")
    print("=" * 50)
    
    print("\n📋 Raw Environment Variables:")
    ebay_vars = [
        'EBAY_CLIENT_ID', 'EBAY_CLIENT_SECRET', 'EBAY_REFRESH_TOKEN',
        'EBAY_PRODUCTION_APP_ID', 'EBAY_PRODUCTION_CLIENT_SECRET', 'EBAY_PRODUCTION_REFRESH_TOKEN'
    ]
    for var in ebay_vars:
        value = os.environ.get(var)
        print(f"  {var}: {'✅ Set' if value else '❌ Missing'}")
        if value and 'TOKEN' in var:
            print(f"    Length: {len(value)} chars")
    
    print("\n🔧 Credential Manager Internal State:")
    print(f"  ebay_app_id: {credential_manager.credentials.get('ebay_app_id')}")
    print(f"  ebay_cert_id: {credential_manager.credentials.get('ebay_cert_id')}")
    print(f"  ebay_client_secret: {credential_manager.credentials.get('ebay_client_secret')}")
    print(f"  ebay_refresh_token: {'✅ Set' if credential_manager.credentials.get('ebay_refresh_token') else '❌ Missing'}")
    
    print("\n🔍 eBay Credential Retrieval:")
    ebay_creds = credential_manager.get_ebay_credentials()
    for key, value in ebay_creds.items():
        if 'token' in key.lower():
            print(f"  {key}: {'✅ Set' if value else '❌ Missing'}")
        else:
            print(f"  {key}: {value}")
    
    print("\n✅ Debug Complete!")

if __name__ == "__main__":
    debug_credentials()
