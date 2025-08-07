#!/usr/bin/env python3
"""
Test the Railway deployed AI endpoint with actual functionality
"""

import requests
import json
import base64
from pathlib import Path

RAILWAY_URL = "https://restyleproject-production.up.railway.app"

def test_ai_endpoint_detailed():
    """Test AI endpoint with more detailed payload"""
    print("🧠 DETAILED AI ENDPOINT TEST")
    print("="*50)
    
    # Test the actual AI endpoint that mobile app uses
    endpoint = "/core/ai/advanced-search/"
    
    # Create a test payload similar to what mobile app sends
    test_payload = {
        "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",  # 1x1 pixel PNG
        "intelligent_crop": True,
        "use_advanced_ai": False  # Use standard AI first
    }
    
    try:
        print(f"📤 Sending request to: {RAILWAY_URL}{endpoint}")
        print(f"📦 Payload: intelligent_crop={test_payload['intelligent_crop']}, use_advanced_ai={test_payload['use_advanced_ai']}")
        
        response = requests.post(
            f"{RAILWAY_URL}{endpoint}",
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("🎉 SUCCESS! AI endpoint is working!")
            data = response.json()
            print(f"📋 Response Data: {json.dumps(data, indent=2)}")
            
        elif response.status_code == 503:
            print("⚠️  Service Unavailable - Expected for advanced AI")
            try:
                data = response.json()
                print(f"📋 Error Details: {json.dumps(data, indent=2)}")
            except:
                print(f"📋 Raw Response: {response.text}")
                
        elif response.status_code == 400:
            print("🔧 Bad Request - Need to fix payload format")
            try:
                data = response.json()
                print(f"📋 Error Details: {json.dumps(data, indent=2)}")
            except:
                print(f"📋 Raw Response: {response.text}")
                
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"📋 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (30s) - Backend might be processing")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - Check Railway deployment")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_alternative_ai_endpoints():
    """Test other potential AI endpoints"""
    print("\n🔍 TESTING ALTERNATIVE AI ENDPOINTS")
    print("="*50)
    
    alternative_endpoints = [
        "/api/ai/search/",
        "/core/ai/search/", 
        "/api/core/ai/search/",
        "/ai/analyze/",
        "/core/analyze/"
    ]
    
    for endpoint in alternative_endpoints:
        try:
            response = requests.get(f"{RAILWAY_URL}{endpoint}", timeout=5)
            status = "✅" if response.status_code in [200, 405] else "❌"
            
            if response.status_code == 405:
                status_text = "Method Not Allowed (POST probably required)"
            elif response.status_code == 404:
                status_text = "Not Found"
            elif response.status_code == 200:
                status_text = "Found!"
            else:
                status_text = f"Status {response.status_code}"
                
            print(f"{status} {endpoint}: {status_text}")
            
        except Exception as e:
            print(f"❌ {endpoint}: ERROR")

def test_ai_service_status():
    """Get detailed AI service status"""
    print("\n🔬 DETAILED AI SERVICE STATUS")
    print("="*50)
    
    try:
        response = requests.get(f"{RAILWAY_URL}/core/ai/status/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("📊 AI Services Status:")
            
            services = data.get('services', {})
            for service, status in services.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {service}: {'Available' if status else 'Not Available'}")
                
            print(f"\n🕒 Timestamp: {data.get('timestamp', 'Unknown')}")
            
        else:
            print(f"❌ Failed to get AI status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting AI status: {e}")

def main():
    print("🧪 RAILWAY AI FUNCTIONALITY TEST")
    print("="*60)
    
    test_ai_service_status()
    test_ai_endpoint_detailed()
    test_alternative_ai_endpoints()
    
    print("\n" + "="*60)
    print("🎯 AI TESTING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
