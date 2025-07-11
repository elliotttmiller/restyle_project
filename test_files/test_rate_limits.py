#!/usr/bin/env python3
"""
Test script to verify eBay rate limit checking functionality
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
from core.tasks import check_ebay_rate_limits, should_skip_api_call

def test_rate_limit_checking():
    print("🧪 Testing eBay Rate Limit Checking...")
    
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
    
    # Test 1: Direct rate limit check
    print("\n1. Testing direct rate limit check...")
    rate_limit_data = check_ebay_rate_limits()
    
    if rate_limit_data:
        print("✅ Rate limit check successful!")
        print(f"Rate limit data: {json.dumps(rate_limit_data, indent=2)}")
        
        # Parse the rate limit data
        try:
            rate_limits = rate_limit_data.get('getRateLimitsResponse', [{}])[0].get('rateLimits', [])
            
            for api_limit in rate_limits:
                api_name = api_limit.get('apiName', '')
                api_context = api_limit.get('apiContext', '')
                api_version = api_limit.get('apiVersion', '')
                
                print(f"\n📊 API: {api_name} (Context: {api_context}, Version: {api_version})")
                
                resources = api_limit.get('resources', [])
                for resource in resources:
                    resource_name = resource.get('name', '')
                    print(f"  Resource: {resource_name}")
                    
                    rates = resource.get('rates', [])
                    for rate in rates:
                        remaining = rate.get('remaining', 0)
                        limit = rate.get('limit', 0)
                        reset_time = rate.get('reset', '')
                        time_window = rate.get('timeWindow', 0)
                        
                        print(f"    Rate Limit: {remaining}/{limit} calls remaining")
                        print(f"    Reset Time: {reset_time}")
                        print(f"    Time Window: {time_window} seconds")
                        
                        # Calculate usage percentage
                        if limit > 0:
                            usage_pct = ((limit - remaining) / limit) * 100
                            print(f"    Usage: {usage_pct:.1f}%")
                        
                        # Determine status
                        if remaining <= 2:
                            print(f"    Status: ⚠️  CRITICAL - Very few calls remaining")
                        elif remaining <= 5:
                            print(f"    Status: ⚠️  WARNING - Low calls remaining")
                        else:
                            print(f"    Status: ✅ HEALTHY - Good calls remaining")
                            
        except Exception as e:
            print(f"❌ Error parsing rate limit data: {e}")
    else:
        print("❌ Rate limit check failed")
    
    # Test 2: Should skip API call check
    print("\n2. Testing should_skip_api_call function...")
    should_skip = should_skip_api_call()
    print(f"Should skip API call: {should_skip}")
    
    if should_skip:
        print("⚠️  Rate limits indicate we should skip the API call")
    else:
        print("✅ Rate limits allow us to proceed with API call")
    
    # Test 3: Manual rate limit check (if the function doesn't work)
    print("\n3. Testing manual rate limit check...")
    headers = {
        'X-EBAY-SOA-OPERATION-NAME': 'getRateLimits',
        'X-EBAY-SOA-SECURITY-APPNAME': app_id,
        'X-EBAY-SOA-RESPONSE-DATA-FORMAT': 'JSON',
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Manual rate limit check successful!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Manual rate limit check failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error in manual rate limit check: {e}")
    
    return True

if __name__ == "__main__":
    test_rate_limit_checking() 