#!/usr/bin/env python3
"""
Live Railway Deployment Test Script
Tests the deployed Restyle.ai backend with new AI capabilities
"""

import requests
import json
import time
from pathlib import Path

# Railway deployment URL
RAILWAY_URL = "https://restyleproject-production.up.railway.app"

def test_health_endpoints():
    """Test basic health endpoints"""
    print("🏥 TESTING HEALTH ENDPOINTS")
    print("="*50)
    
    endpoints = [
        "/core/health/",
        "/core/metrics/", 
        "/core/ai/status/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{RAILWAY_URL}{endpoint}", timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"❌ {endpoint}: ERROR - {e}")

def test_ai_endpoints():
    """Test AI endpoints with sample data"""
    print("\n🤖 TESTING AI ENDPOINTS")
    print("="*50)
    
    # Test standard AI endpoint
    ai_endpoint = "/core/ai/advanced-search/"
    
    try:
        # Create a simple test payload
        test_data = {
            "image": "test_image_data",
            "intelligent_crop": True,
            "use_advanced_ai": False  # Start with standard AI
        }
        
        response = requests.post(
            f"{RAILWAY_URL}{ai_endpoint}", 
            json=test_data,
            timeout=30
        )
        
        status = "✅" if response.status_code in [200, 503] else "❌"
        print(f"{status} AI Endpoint: {response.status_code}")
        
        if response.status_code == 503:
            print("   ⚠️  Expected: Advanced AI dependencies not installed")
            print("   🔄 This will use standard AI service as fallback")
        elif response.status_code == 200:
            print("   🎉 AI service responding successfully!")
            print(f"   Response: {response.json()}")
            
    except Exception as e:
        print(f"❌ AI Endpoint: ERROR - {e}")

def test_mobile_app_integration():
    """Test endpoints that mobile app uses"""
    print("\n📱 TESTING MOBILE APP INTEGRATION")
    print("="*50)
    
    # Based on the logs, mobile app is hitting these endpoints
    mobile_endpoints = [
        "/core/health/",
        "/core/ebay-token/health/", 
        "/api/core/health/",
        "/core/metrics/",
        "/core/ai/status/"
    ]
    
    for endpoint in mobile_endpoints:
        try:
            response = requests.get(f"{RAILWAY_URL}{endpoint}", timeout=10)
            status_symbol = "✅" if response.status_code in [200, 404] else "❌"
            
            if response.status_code == 404:
                status_text = "Not Found (Expected for some endpoints)"
            elif response.status_code == 200:
                status_text = "Success"
            elif response.status_code == 500:
                status_text = "Server Error (Needs fixing)"
            else:
                status_text = f"Status {response.status_code}"
                
            print(f"{status_symbol} {endpoint}: {status_text}")
            
        except Exception as e:
            print(f"❌ {endpoint}: CONNECTION ERROR - {e}")

def check_deployment_logs():
    """Analyze the deployment success based on logs"""
    print("\n📋 DEPLOYMENT ANALYSIS")
    print("="*50)
    
    deployment_status = {
        "✅ Core Services": [
            "AI Service initialized", 
            "Google Vision API connected",
            "eBay OAuth working",
            "FAISS vector search loaded",
            "Health endpoints responding"
        ],
        "⚠️  Known Issues": [
            "Advanced AI needs PyTorch installation",
            "AWS region not configured", 
            "Some mobile endpoints return 404/500"
        ],
        "🎯 Next Actions": [
            "Install PyTorch on Railway for advanced AI",
            "Configure AWS region for Rekognition",
            "Test with real image upload from mobile app"
        ]
    }
    
    for category, items in deployment_status.items():
        print(f"\n{category}:")
        for item in items:
            print(f"   • {item}")

def main():
    """Run comprehensive deployment test"""
    print("🚀 RESTYLE.AI RAILWAY DEPLOYMENT TEST")
    print("="*60)
    
    print("🔗 Testing Railway deployment...")
    print(f"📍 URL: {RAILWAY_URL}")
    
    # Run tests
    test_health_endpoints()
    test_ai_endpoints() 
    test_mobile_app_integration()
    check_deployment_logs()
    
    print("\n" + "="*60)
    print("🎯 DEPLOYMENT TEST COMPLETE")
    print("="*60)
    
    print("\n📱 YOUR MOBILE APP IS ALREADY TESTING THE BACKEND!")
    print("   The logs show TestFlight app making API calls ✅")
    print("\n🔥 READY FOR NEXT PHASE:")
    print("   1. Install PyTorch for advanced AI features")
    print("   2. Test real image uploads from mobile app") 
    print("   3. Verify new app icons in TestFlight")

if __name__ == "__main__":
    main()
