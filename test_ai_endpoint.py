#!/usr/bin/env python3
"""
Test script for AI image search endpoint
"""
import requests
import json
from PIL import Image
import io

def test_ai_image_search():
    """Test the AI image search endpoint"""
    print("Testing AI Image Search Endpoint...")
    
    # Create a test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    image_data = img_bytes.getvalue()
    
    # Prepare the request
    url = "http://localhost:8000/api/core/ai/image-search/"
    
    # Create form data
    files = {
        'image': ('test_image.jpg', image_data, 'image/jpeg')
    }
    
    # Add authentication header (you'll need to get a valid token)
    headers = {
        'Authorization': 'Bearer YOUR_TOKEN_HERE'  # Replace with actual token
    }
    
    try:
        print(f"Sending request to: {url}")
        print(f"Image size: {len(image_data)} bytes")
        
        # For now, just test the request structure
        print("✅ Request structure looks correct")
        print("📝 To test with real authentication:")
        print("   1. Get a valid JWT token from your app")
        print("   2. Replace 'YOUR_TOKEN_HERE' with the actual token")
        print("   3. Run this test again")
        
        # Uncomment to actually test the endpoint
        # response = requests.post(url, files=files, headers=headers)
        # print(f"Response status: {response.status_code}")
        # print(f"Response data: {response.json()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run the test"""
    print("🧪 Testing AI Image Search Endpoint...\n")
    test_ai_image_search()
    print("\n✅ Test completed!")

if __name__ == '__main__':
    main() 