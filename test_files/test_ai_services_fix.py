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

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set up environment variables
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIATJEIK57QFHCF5KUJ'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
os.environ['AWS_REGION_NAME'] = 'us-east-1'

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
        
        # Set up credentials
        credentials_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'silent-polygon-465403-h9-3a57d36afc97.json')
        if os.path.exists(credentials_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            print("✅ Google Cloud credentials found")
        else:
            print("❌ Google Cloud credentials not found")
            return False
        
        client = vision.ImageAnnotatorClient()
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
        url = "http://localhost:8000/api/core/ai/advanced-search/"
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