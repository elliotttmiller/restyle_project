#!/usr/bin/env python3
"""
Test script to check Google Cloud API key permissions and project setup
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key_info():
    """Test API key permissions using a simple API call"""
    try:
        from google.cloud import vision
        import base64
        
        google_api_key = os.environ.get('GOOGLE_API_KEY')
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', '609071491201')
        
        print(f"📋 Testing API Key Information...")
        print(f"   Project ID: {project_id}")
        print(f"   API Key: {'SET' if google_api_key else 'NOT SET'}")
        
        if not google_api_key:
            print("❌ No GOOGLE_API_KEY found")
            return False
            
        # Create client
        client_options = {
            "api_key": google_api_key,
            "quota_project_id": project_id
        }
        
        client = vision.ImageAnnotatorClient(client_options=client_options)
        print("✅ Vision client created successfully")
        
        # Try a minimal test image (1x1 white pixel)
        print("🔍 Testing with minimal image...")
        
        # Create a minimal 1x1 white PNG image in base64
        minimal_png = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGAMa6g9wAAAABJRU5ErkJggg=='
        
        image = vision.Image(content=minimal_png)
        
        # Try text detection (simplest operation)
        response = client.text_detection(image=image)
        print("✅ Text detection call successful")
        
        if response.error.message:
            print(f"⚠️  API returned error: {response.error.message}")
        else:
            print("✅ No errors in response")
            
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ API test failed: {error_str}")
        
        # Check for specific error types
        if "API_KEY_SERVICE_BLOCKED" in error_str:
            print("🔍 Analysis: API key is blocked for Vision API")
            print("   Solution: Enable Vision API for this project in Google Cloud Console")
        elif "API_KEY_INVALID" in error_str:
            print("🔍 Analysis: API key is invalid")
            print("   Solution: Check API key format and regenerate if needed")
        elif "PERMISSION_DENIED" in error_str:
            print("🔍 Analysis: Permission denied")
            print("   Solution: Check API key permissions and project access")
        else:
            print("🔍 Analysis: Unknown error - check Google Cloud Console")
            
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Vision API Key Permissions...")
    print("=" * 60)
    
    success = test_api_key_info()
    
    print("=" * 60)
    if success:
        print("✅ API key test PASSED")
    else:
        print("❌ API key test FAILED")
        print("\n💡 Next steps:")
        print("   1. Go to Google Cloud Console")
        print("   2. Select project 609071491201")
        print("   3. Enable Vision API")
        print("   4. Check API key restrictions")
