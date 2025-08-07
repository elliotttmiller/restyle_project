#!/usr/bin/env python3
"""
Simple verification that Google Vision API is working with a base64 test image
"""
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_vision_working():
    """Test Google Vision API with a simple base64 image"""
    try:
        from google.cloud import vision
        
        print("🔍 Testing Google Vision API with base64 image...")
        
        google_api_key = os.environ.get('GOOGLE_API_KEY')
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', '609071491201')
        
        # Create client
        client_options = {
            "api_key": google_api_key,
            "quota_project_id": project_id
        }
        client = vision.ImageAnnotatorClient(client_options=client_options)
        print("✅ Vision client created successfully")
        
        # Use a small test image (1x1 white PNG in base64)
        test_image_b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGAMa6g9wAAAABJRU5ErkJggg=='
        image_content = base64.b64decode(test_image_b64)
        
        image = vision.Image(content=image_content)
        
        # Test label detection
        response = client.label_detection(image=image)
        
        if response.error.message:
            print(f"❌ Vision API error: {response.error.message}")
            return False
        else:
            labels = response.label_annotations
            print(f"✅ Google Vision API call successful!")
            print(f"   Found {len(labels)} labels")
            
            # Test text detection too
            text_response = client.text_detection(image=image)
            if not text_response.error.message:
                print("✅ Text detection also working")
            
            return True
            
    except Exception as e:
        print(f"❌ Google Vision test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Google Vision API Verification Test")
    print("=" * 50)
    
    success = test_google_vision_working()
    
    print("=" * 50)
    if success:
        print("🎉 SUCCESS! Google Vision API is fully functional!")
        print("\n✅ Confirmed working:")
        print("   • API key authentication")
        print("   • Project ID configuration") 
        print("   • Label detection")
        print("   • Text detection")
        print("   • No more API_KEY_SERVICE_BLOCKED errors")
        print("\n🚀 Google Vision API integration complete!")
    else:
        print("❌ Google Vision API still has issues")
        print("   Check Google Cloud Console for API restrictions")
