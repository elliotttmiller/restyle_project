#!/usr/bin/env python3
"""
Test script to check Google Vision client creation only
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_vision_client_creation():
    """Test if we can create a Vision client without making API calls"""
    try:
        from google.cloud import vision
        
        google_api_key = os.environ.get('GOOGLE_API_KEY')
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', '609071491201')
        
        print(f"📋 Testing Vision client creation...")
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
        
        # Try to access client properties (should not make API calls)
        print(f"   Client type: {type(client)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vision client creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Vision Client Creation Only...")
    print("=" * 50)
    
    success = test_vision_client_creation()
    
    print("=" * 50)
    if success:
        print("✅ Vision client creation test PASSED")
    else:
        print("❌ Vision client creation test FAILED")
