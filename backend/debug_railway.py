#!/usr/bin/env python3
"""
Debug script for Railway deployment issues
"""
import requests
import time
import sys
import json

def test_railway_connectivity():
    """Test various aspects of Railway connectivity"""
    base_url = "https://restyleproject-production.up.railway.app"
    
    print("🔍 Railway Debug Diagnostics")
    print("=" * 50)
    print(f"Testing URL: {base_url}")
    print()
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.status_code == 200:
            print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   Error: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 2: Health endpoint specifically
    print("2. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text}")
        else:
            print(f"   Error: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 3: Test with different ports
    print("3. Testing alternative ports...")
    for port in [8000, 8080, 3000]:
        try:
            alt_url = f"https://restyleproject-production.up.railway.app:{port}"
            response = requests.get(alt_url, timeout=5)
            print(f"   Port {port}: {response.status_code}")
        except:
            print(f"   Port {port}: Connection failed")
    
    print()
    
    # Test 4: Check Railway status
    print("4. Railway service status check...")
    print("   Please check your Railway dashboard for:")
    print("   - Service status (should be 'Active')")
    print("   - Recent deployments (should be successful)")
    print("   - Container logs (should show Django running)")
    print("   - Environment variables (PORT should be set)")
    
    print()
    print("5. Configuration check:")
    print("   - Start Command should be: python start.py")
    print("   - Target Port should be: 8000")
    print("   - Serverless should be: Disabled")
    print("   - Healthcheck Path should be: /health")

if __name__ == '__main__':
    test_railway_connectivity() 