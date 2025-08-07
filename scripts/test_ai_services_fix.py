#!/usr/bin/env python3
"""
Test script to verify AI services are working with the new credentials
"""
import os
import sys
import requests
import base64
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_aws_rekognition():
    """Test AWS Rekognition service"""
    try:
        import boto3
        print("✅ boto3 imported successfully")
        
        # Create a simple test image (1x1 pixel)
        test_image = Image.new('RGB', (1, 1), color='red')
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        rekognition = boto3.client(
            'rekognition',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION_NAME', 'us-east-1')
        )
        
        print("✅ AWS Rekognition client created successfully")
        
        # Test label detection
        response = rekognition.detect_labels(
            Image={'Bytes': img_byte_arr},
            MaxLabels=5,
            MinConfidence=50
        )
        
        print("✅ AWS Rekognition label detection successful")
        print(f"   Found {len(response['Labels'])} labels")
        return True
        
    except Exception as e:
        print(f"❌ AWS Rekognition test failed: {e}")
        return False

def test_google_vision():
    """Test Google Vision API"""
    try:
        from google.cloud import vision
        
        # Set up credentials using API key
        google_api_key = os.environ.get('GOOGLE_API_KEY')
        if not google_api_key:
            print("❌ No GOOGLE_API_KEY found")
            return False
            
        print("✅ Google Cloud credentials found")
        
        client_options = {
            "api_key": google_api_key,
            "quota_project_id": "609071491201"  # Our correct project ID
        }
        client = vision.ImageAnnotatorClient(client_options=client_options)
        print("✅ Google Vision client created successfully")
        
        # Create a simple test image
        test_image = Image.new('RGB', (10, 10), color='blue')
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        image = vision.Image(content=img_byte_arr)
        response = client.label_detection(image=image)
        
        print("✅ Google Vision API test successful")
        print(f"   Found {len(response.label_annotations)} labels")
        return True
        
    except Exception as e:
        print(f"❌ Google Vision API test failed: {e}")
        return False

def test_backend_ai_endpoint():
    """Test the backend AI endpoint"""
    try:
        # Create a simple test image
        test_image = Image.new('RGB', (10, 10), color='green')
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Test the advanced AI search endpoint
        railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'restyleproject-production.up.railway.app')
        url = f"https://{railway_domain}/core/ai/advanced-search/"
        files = {'image': ('test.png', img_byte_arr, 'image/png')}
        
        response = requests.post(url, files=files, timeout=30)
        
        if response.status_code == 200:
            print("✅ Backend AI endpoint test successful")
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            return True
        else:
            print(f"❌ Backend AI endpoint test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend AI endpoint test failed: {e}")
        return False

def main():
    """Run all AI service tests"""
    print("🧪 Testing AI Services...")
    print("=" * 50)
    
    results = []
    
    # Test AWS Rekognition
    print("\n1. Testing AWS Rekognition...")
    results.append(("AWS Rekognition", test_aws_rekognition()))
    
    # Test Google Vision
    print("\n2. Testing Google Vision API...")
    results.append(("Google Vision", test_google_vision()))
    
    # Test Backend AI Endpoint
    print("\n3. Testing Backend AI Endpoint...")
    results.append(("Backend AI", test_backend_ai_endpoint()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for service, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{service:20} {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} services working")
    
    if passed == total:
        print("🎉 All AI services are working properly!")
    else:
        print("⚠️  Some AI services need attention")

if __name__ == "__main__":
    main() 