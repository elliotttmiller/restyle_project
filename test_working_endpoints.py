#!/usr/bin/env python3
"""
Test only the working endpoints
"""


import requests
import json
import time
import logging

BASE_URL = "https://restyleproject-production.up.railway.app"
logger = logging.getLogger(__name__)

def test_health():
    """Test the /health endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    logger.info(f"/health status: {response.status_code}")
    assert response.status_code == 200, f"/health failed: {response.text}"

def test_core_health():
    """Test the /api/core/health/ endpoint."""
    response = requests.get(f"{BASE_URL}/api/core/health/")
    logger.info(f"/api/core/health/ status: {response.status_code}")
    assert response.status_code == 200, f"/api/core/health/ failed: {response.text}"

def test_ai_status():
    """Test the /api/core/ai/status/ endpoint."""
    response = requests.get(f"{BASE_URL}/api/core/ai/status/")
    logger.info(f"/api/core/ai/status/ status: {response.status_code}")
    assert response.status_code == 200, f"/api/core/ai/status/ failed: {response.text}"

def test_user_registration():
    """Test user registration endpoint."""
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
    logger.info(f"/api/users/register/ status: {response.status_code}")
    assert response.status_code == 201, f"/api/users/register/ failed: {response.text}"

def test_token_endpoint():
    """Test token endpoint after registering a user."""
    test_user = {
        "username": f"tokentest_{int(time.time())}",
        "email": "token@example.com",
        "password": "testpass123"
    }
    requests.post(f"{BASE_URL}/api/users/register/", json=test_user)
    response = requests.post(
        f"{BASE_URL}/api/token/",
        json={"username": test_user["username"], "password": test_user["password"]},
        headers={"Content-Type": "application/json"}
    )
    logger.info(f"/api/token/ status: {response.status_code}")
    assert response.status_code == 200, f"/api/token/ failed: {response.text}"

def test_ebay_search_get():
    """Test eBay search endpoint."""
    response = requests.get(f"{BASE_URL}/api/core/ebay-search/?q=nike+shoes&limit=3")
    logger.info(f"/api/core/ebay-search/ status: {response.status_code}")
    assert response.status_code == 200, f"/api/core/ebay-search/ failed: {response.text}"

def test_advanced_search_with_image():
    """Test advanced search with a sample image."""
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
    logger.info(f"/api/core/ai/advanced-search/ status: {response.status_code}")
    assert response.status_code in [200, 503], f"/api/core/ai/advanced-search/ failed: {response.text}"

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
    import logging
    logger = logging.getLogger(__name__)
    for name, test_func in tests:
        try:
            test_func()
            results[name] = True
        except AssertionError as e:
            logger.error(f"Test {name} failed: {e}")
            results[name] = False
        except Exception as e:
            logger.error(f"Test {name} raised an unexpected exception: {e}")
            results[name] = False
    logger.info("\n" + "=" * 40)
    logger.info("RESULTS:")
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        logger.info(f"{name:<25} {status}")
    passed = sum(results.values())
    total = len(results)
    logger.info(f"\nOverall: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()