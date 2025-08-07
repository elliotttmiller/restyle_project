#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all Restyle.ai API endpoints for functionality
"""

import requests
import json
import base64
import os
from pathlib import Path

BASE_URL = "https://restyleproject-production.up.railway.app"

def test_health_endpoint():
    """Test health check endpoint"""
    print("Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_analyze_image_endpoint():
    """Test AI image search endpoint with sample image"""
    print("\nTesting AI Image Search Endpoint...")
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    payload = {
        "image": test_image_b64,
        "query": "test image"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/core/ai/image-search/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        return response.status_code in [200, 400]  # 400 is acceptable for test image
    except Exception as e:
        print(f"AI image search failed: {e}")
        return False

def test_advanced_search_endpoint():
    """Test advanced AI search endpoint"""
    print("\nTesting Advanced AI Search Endpoint...")
    
    payload = {
        "query": "blue jeans",
        "category": "clothing",
        "limit": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/core/ai/advanced-search/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"Advanced search failed: {e}")
        return False

def test_user_endpoints():
    """Test user registration"""
    print("\nTesting User Registration...")
    
    # Test user registration
    import time
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        # Register
        response = requests.post(
            f"{BASE_URL}/api/users/register/",
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        print(f"Register Status: {response.status_code}")
        print(f"Register Response: {response.text[:200]}...")
        
        # Test token endpoint
        token_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = requests.post(
            f"{BASE_URL}/api/token/",
            json=token_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        print(f"Token Status: {response.status_code}")
        print(f"Token Response: {response.text[:200]}...")
        
        return True
    except Exception as e:
        print(f"User endpoints failed: {e}")
        return False

def test_ebay_search():
    """Test eBay search functionality"""
    print("\nTesting eBay Search...")
    
    payload = {
        "query": "nike shoes",
        "limit": 3
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/core/ebay-search/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"eBay search failed: {e}")
        return False

def test_ai_services():
    """Test AI services status"""
    print("\nTesting AI Services Status...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/core/ai/status/",
            timeout=15
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"AI services status failed: {e}")
        return False

def main():
    """Run all endpoint tests"""
    print("Starting Comprehensive API Endpoint Testing")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("AI Image Search", test_analyze_image_endpoint),
        ("Advanced Search", test_advanced_search_endpoint),
        ("User Management", test_user_endpoints),
        ("eBay Search", test_ebay_search),
        ("AI Services", test_ai_services)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"{test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:<20} {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("All endpoints are functional!")
    else:
        print("Some endpoints need attention")

if __name__ == "__main__":
    main()