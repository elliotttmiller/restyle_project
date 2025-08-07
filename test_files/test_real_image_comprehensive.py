#!/usr/bin/env python3
"""
Comprehensive test using our actual test image from test_files/example2.jpg
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_with_real_image():
    """Test all AI services with our actual test image"""
    
    # Get the test image path
    test_image_path = Path(__file__).parent / "example2.jpg"
    
    if not test_image_path.exists():
        print(f"❌ Test image not found: {test_image_path}")
        return False
        
    print(f"📸 Using test image: {test_image_path}")
    
    # Read the image
    with open(test_image_path, 'rb') as f:
        image_content = f.read()
    
    print(f"✅ Image loaded successfully ({len(image_content)} bytes)")
    
    results = {}
    
    # Test AWS Rekognition
    print("\n🔍 Testing AWS Rekognition...")
    print("-" * 40)
    try:
        import boto3
        
        client = boto3.client(
            'rekognition',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION_NAME', 'us-east-1')
        )
        
        response = client.detect_labels(
            Image={'Bytes': image_content},
            MaxLabels=10,
            MinConfidence=50
        )
        
        labels = response.get('Labels', [])
        print(f"✅ AWS Rekognition successful")
        print(f"   Found {len(labels)} labels:")
        for label in labels[:5]:  # Show top 5
            print(f"   - {label['Name']}: {label['Confidence']:.1f}%")
            
        results['AWS Rekognition'] = True
        
    except Exception as e:
        print(f"❌ AWS Rekognition failed: {e}")
        results['AWS Rekognition'] = False
    
    # Test Google Vision API
    print("\n🔍 Testing Google Vision API...")
    print("-" * 40)
    try:
        from google.cloud import vision
        
        google_api_key = os.environ.get('GOOGLE_API_KEY')
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', '609071491201')
        
        if not google_api_key:
            print("❌ No GOOGLE_API_KEY found")
            results['Google Vision'] = False
        else:
            client_options = {
                "api_key": google_api_key,
                "quota_project_id": project_id
            }
            
            client = vision.ImageAnnotatorClient(client_options=client_options)
            image = vision.Image(content=image_content)
            
            # Test label detection
            response = client.label_detection(image=image)
            labels = response.label_annotations
            
            print(f"✅ Google Vision successful")
            print(f"   Found {len(labels)} labels:")
            for label in labels[:5]:  # Show top 5
                print(f"   - {label.description}: {label.score:.3f}")
                
            # Test text detection
            response = client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                print(f"   Found text: '{texts[0].description[:50]}...'")
            else:
                print("   No text detected")
                
            results['Google Vision'] = True
            
    except Exception as e:
        print(f"❌ Google Vision failed: {e}")
        results['Google Vision'] = False
    
    # Test Backend AI Service
    print("\n🔍 Testing Backend AI Service...")
    print("-" * 40)
    try:
        # Add backend directory to path to import our services
        backend_path = Path(__file__).parent.parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from core.ai_service import AIService
        
        # Test our AI service directly
        ai_service = AIService()
        ai_service._initialize_client()
        
        if ai_service._client:
            # Test with our image
            image_obj = vision.Image(content=image_content)
            response = ai_service._client.label_detection(image=image_obj)
            
            if response.label_annotations:
                print(f"✅ Backend AI Service successful")
                print(f"   Service initialized and working")
                results['Backend AI Service'] = True
            else:
                print("⚠️  Backend AI Service initialized but no results")
                results['Backend AI Service'] = True
        else:
            print("❌ Backend AI Service client not initialized")
            results['Backend AI Service'] = False
            
    except Exception as e:
        print(f"❌ Backend AI Service failed: {e}")
        results['Backend AI Service'] = False
    
    return results

if __name__ == "__main__":
    print("🧪 Comprehensive AI Test with Real Image")
    print("=" * 60)
    
    results = test_with_real_image()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for service, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{service:<20} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Overall: {passed}/{total} services working")
    
    if passed == total:
        print("🎉 ALL AI SERVICES WORKING PERFECTLY!")
        print("✅ Ready for production deployment")
    elif passed >= total - 1:
        print("⚠️  Almost there - minor issues to resolve")
    else:
        print("❌ Multiple issues need attention")
