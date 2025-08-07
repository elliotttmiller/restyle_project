#!/usr/bin/env python3
"""
Test script to verify Railway endpoints
"""
import requests
import time
import sys

def test_endpoint(base_url, endpoint, description):
    """Test a specific endpoint"""
    url = f"{base_url}{endpoint}"
    try:
        print(f"Testing {description}...")
        response = requests.get(url, timeout=30)
        print(f"✓ {description}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Response: {data}")
        else:
            print(f"  Error: {response.text}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"✗ {description}: Error - {e}")
        return False

def main():
    """Test all endpoints"""
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://restyleproject-production.up.railway.app"
    
    print(f"Testing Railway endpoints at: {base_url}")
    print("=" * 50)
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check (no trailing slash)"),
        ("/health/", "Health check (with trailing slash)"),
        ("/test/", "Test endpoint"),
    ]
    
    all_passed = True
    for endpoint, description in endpoints:
        if not test_endpoint(base_url, endpoint, description):
            all_passed = False
        print()
    
    if all_passed:
        print("✅ All endpoints are working!")
    else:
        print("❌ Some endpoints failed")
        sys.exit(1)

if __name__ == '__main__':
    main() 