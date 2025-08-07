#!/usr/bin/env python3
"""
Test script to verify Django loads .env automatically
"""
import os
import sys
import django

# Setup Django (should auto-load .env now)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_env_loading():
    """Test that Django loads environment variables automatically"""
    print("🧪 Testing Automatic .env Loading")
    print("=" * 50)
    
    # Test key environment variables
    test_vars = [
        'EBAY_CLIENT_ID',
        'EBAY_CLIENT_SECRET', 
        'EBAY_REFRESH_TOKEN',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'GOOGLE_API_KEY'
    ]
    
    print("\n📋 Environment Variables Status:")
    for var in test_vars:
        value = os.environ.get(var)
        status = "✅ Loaded" if value else "❌ Missing"
        print(f"  {var}: {status}")
    
    print("\n✅ Environment Loading Test Complete!")

if __name__ == "__main__":
    test_env_loading()
