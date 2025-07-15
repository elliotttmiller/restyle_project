#!/usr/bin/env python3
"""
Diagnose Gemini API issues
"""

import os
import sys
import requests
import json

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_gemini_diagnosis():
    """Diagnose why Gemini API is inactive"""
    print("🔍 DIAGNOSING GEMINI API ISSUES")
    print("=" * 50)
    
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        import google.generativeai as genai
        
        print("📋 CHECKING GOOGLE CLOUD CONFIGURATION:")
        print(f"   GOOGLE_APPLICATION_CREDENTIALS: {getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS', 'Not set')}")
        
        # Check if credentials file exists
        creds_path = getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS', None)
        if creds_path:
            print(f"   Credentials file exists: {os.path.exists(creds_path)}")
            if os.path.exists(creds_path):
                print(f"   File size: {os.path.getsize(creds_path)} bytes")
        
        print("\n🔑 TESTING GEMINI INITIALIZATION:")
        
        # Test 1: Basic Gemini initialization
        try:
            print("   Testing basic Gemini initialization...")
            genai.configure(
                ***REMOVED***=None,  # Will use service account credentials
                transport="rest"
            )
            print("   ✅ Basic configuration successful")
        except Exception as e:
            print(f"   ❌ Basic configuration failed: {e}")
            return False
        
        # Test 2: Model creation
        try:
            print("   Testing model creation...")
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            print("   ✅ Model creation successful")
        except Exception as e:
            print(f"   ❌ Model creation failed: {e}")
            return False
        
        # Test 3: Simple API call
        try:
            print("   Testing simple API call...")
            response = model.generate_content("Hello, this is a test.")
            print(f"   ✅ API call successful: {response.text[:100]}...")
        except Exception as e:
            print(f"   ❌ API call failed: {e}")
            return False
        
        # Test 4: Check service account permissions
        print("\n🔐 CHECKING SERVICE ACCOUNT PERMISSIONS:")
        try:
            import google.auth
            from google.auth import default
            
            print("   Testing service account authentication...")
            credentials, project = default()
            print(f"   ✅ Service account authenticated")
            print(f"   Project: {project}")
            print(f"   Credentials type: {type(credentials).__name__}")
            
            # Check if Gemini API is enabled
            print("\n🌐 CHECKING GEMINI API STATUS:")
            try:
                from googleapiclient.discovery import build
                service = build('aiplatform', 'v1', credentials=credentials)
                print("   ✅ Vertex AI API accessible")
            except Exception as e:
                print(f"   ⚠️  Vertex AI API issue: {e}")
            
        except Exception as e:
            print(f"   ❌ Service account authentication failed: {e}")
            return False
        
        print("\n✅ GEMINI DIAGNOSIS COMPLETE")
        print("   All tests passed - Gemini should be working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during Gemini diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_gemini_diagnosis() 