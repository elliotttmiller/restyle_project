#!/usr/bin/env python3
"""
Debug test for mobile app simulation issues
"""

import os
import requests
import json
from PIL import Image
import io
import urllib3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def debug_mobile_api():
    """Debug the mobile API call step by step"""
    
    print("🔍 DEBUG: Mobile API Test")
    print("=" * 40)
    
    # Step 1: Check environment
    railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', 'restyleproject-production.up.railway.app')
    print(f"Railway domain: {railway_domain}")
    
    base_url = f"https://{railway_domain}/core"
    endpoint = f"{base_url}/ai/advanced-search/"
    print(f"Full endpoint: {endpoint}")
    
    # Step 2: Check test image
    test_image_path = os.path.join(os.path.dirname(__file__), 'example2.jpg')
    print(f"Test image path: {test_image_path}")
    print(f"Image exists: {os.path.exists(test_image_path)}")
    
    if not os.path.exists(test_image_path):
        print("❌ Test image not found!")
        return False
    
    # Step 3: Load and validate image
    try:
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        print(f"Image loaded: {len(image_data)} bytes")
        
        # Validate with PIL
        img = Image.open(io.BytesIO(image_data))
        print(f"Image size: {img.size}")
        print(f"Image mode: {img.mode}")
        print(f"Image format: {img.format}")
        
    except Exception as e:
        print(f"❌ Image loading error: {e}")
        return False
    
    # Step 4: Test API call
    try:
        print("\n🌐 Testing API call...")
        
        files = {'image': ('test.jpg', image_data, 'image/jpeg')}
        data = {'image_type': 'image/jpeg'}
        
        print(f"Making POST request to: {endpoint}")
        response = requests.post(
            endpoint,
            files=files,
            data=data,
            timeout=30,
            verify=False
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ API call successful!")
            try:
                result = response.json()
                print(f"Response keys: {list(result.keys())}")
                return True
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
                print(f"Raw response: {response.text[:500]}")
                return False
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ API call error: {e}")
        return False

if __name__ == "__main__":
    debug_mobile_api()
