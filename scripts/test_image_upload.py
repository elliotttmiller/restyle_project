#!/usr/bin/env python3
"""
Enhanced test script to analyze AI system accuracy
"""
import requests
import os
import json
from datetime import datetime

# Test the image upload to the backend
def test_image_upload():
    # URL of the backend
    url = "https://restyle-backend.onrender.com/api/core/ai/advanced-search/"
    
    # Test image path
    image_path = "test_files/example2.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        return
    
    # Create FormData
    with open(image_path, 'rb') as f:
        files = {'image': ('test.jpg', f, 'image/jpeg')}
        
        print(f"📤 Uploading image to: {url}")
        print(f"📁 Image file: {image_path}")
        
        try:
            response = requests.post(url, files=files)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ Image upload successful!")
                print(f"📊 Response data: {response.json()}")
            else:
                print(f"❌ Image upload failed: {response.status_code}")
                print(f"📄 Error response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error during upload: {e}")

if __name__ == "__main__":
    test_image_upload() 