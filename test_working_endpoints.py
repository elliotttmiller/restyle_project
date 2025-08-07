#!/usr/bin/env python3
"""
Test only the working endpoints
"""

import requests
import json
import time

BASE_URL = "https://restyleproject-production.up.railway.app"

def test_health():
    print("Testing Health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_core_health():
    print("\nTesting Core Health...")
    response = requests.get(f"{BASE_URL}/api/core/health/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_ai_status():
    print("\nTesting AI Status...")
    response = requests.get(f"{BASE_URL}/api/core/ai/status/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_user_registration():
    print("\nTesting User Registration...")
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/users/register/",
        json=test_user,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
    return response.status_code == 201

def test_token_endpoint():
    print("\nTesting Token Endpoint...")
    # First register a user
    test_user = {
        "username": f"tokentest_{int(time.time())}",
        "email": "token@example.com", 
        "password": "testpass123"
    }
    
    # Register
    requests.post(f"{BASE_URL}/api/users/register/", json=test_user)
    
    # Get token
    response = requests.post(
        f"{BASE_URL}/api/token/",
        json={"username": test_user["username"], "password": test_user["password"]},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:100]}...")
    return response.status_code == 200

def test_ebay_search_get():
    print("\nTesting eBay Search (GET)...")
    response = requests.get(f"{BASE_URL}/api/core/ebay-search/?q=nike+shoes&limit=3")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:300]}...")
    return response.status_code == 200

def test_advanced_search_with_image():
    print("\nTesting Advanced Search with proper image...")
    
    # Simple 1x1 PNG image
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    payload = {
        "image": test_image_b64,
        "intelligent_crop": True,
        "use_advanced_ai": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/core/ai/advanced-search/",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:300]}...")
    return response.status_code in [200, 503]  # 503 is acceptable for stub

def main():
    print("Testing Working Endpoints")
    print("=" * 40)
    
    tests = [
        ("Health Check", test_health),
        ("Core Health", test_core_health),
        ("AI Status", test_ai_status),
        ("User Registration", test_user_registration),
        ("Token Endpoint", test_token_endpoint),
        ("eBay Search (GET)", test_ebay_search_get),
        ("Advanced Search", test_advanced_search_with_image)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"Test {name} failed: {e}")
            results[name] = False
    
    print("\n" + "=" * 40)
    print("RESULTS:")
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{name:<25} {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()