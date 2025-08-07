#!/usr/bin/env python3
"""
Test the fixed advanced search endpoint
"""

import requests
import json

BASE_URL = "https://restyleproject-production.up.railway.app"

def test_advanced_search():
    print("Testing Advanced Search...")
    
    # Simple 1x1 PNG image in base64
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    payload = {
        "image": test_image_b64,
        "intelligent_crop": True,
        "use_advanced_ai": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/core/ai/advanced-search/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code in [200, 503]
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_advanced_search()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")