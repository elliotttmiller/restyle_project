#!/usr/bin/env python3
"""
Mobile app simulation test for restyle-mobile AI accuracy.
Simulates the exact behavior of the mobile app through Expo Go using test image.
"""

import os
import sys
import requests
import json
import time
from datetime import datetime
import base64
from PIL import Image
import io
import mimetypes
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def simulate_mobile_app_search():
    """Simulate the exact mobile app image search behavior."""
    
    print("📱 MOBILE APP SIMULATION TEST")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Mobile app configuration (same as mobile app)
    import os
import sys
import json
import time
import requests
from PIL import Image
from datetime import datetime
import urllib3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get Railway domain from environment
RAILWAY_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN', 'restyleproject-production.up.railway.app')
BASE_URL = f"https://{RAILWAY_DOMAIN}/core"

def main():
    """Main test function simulating mobile app behavior"""
    TEST_IMAGE_PATH = r"C:\Users\AMD\restyle_project\test_files\example2.JPG"  # Absolute path
    
    print("📸 STEP 1: Simulating Mobile App Image Selection")
    print("-" * 45)
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
        return False
    
    try:
        # Simulate mobile app image loading (same as mobile app)
        with open(TEST_IMAGE_PATH, 'rb') as f:
            image_data = f.read()
        
        print(f"✅ Test image loaded: {len(image_data)} bytes")
        
        # Analyze image properties (same as mobile app validation)
        with Image.open(TEST_IMAGE_PATH) as img:
            print(f"   Image size: {img.size}")
            print(f"   Image mode: {img.mode}")
            print(f"   Image format: {img.format}")
        
        # Simulate mobile app image validation
        if len(image_data) == 0:
            print("❌ Image validation failed: Empty image data")
            return False
        
        print("✅ Image validation passed (mobile app style)")
        
    except Exception as e:
        print(f"❌ Error loading test image: {e}")
        return False
    
    print()
    print("🔍 STEP 2: Simulating Mobile App API Call")
    print("-" * 40)
    
    # Simulate the exact mobile app API call
    try:
        # Create FormData exactly like mobile app (same format)
        files = {
            'image': ('image.jpg', image_data, 'image/jpeg')  # Same as mobile app
        }
        
        # Add optional parameters like mobile app
        data = {
            'image_type': 'image/jpeg'  # Same as mobile app
        }
        
        print("📤 Sending request to /ai/advanced-search/ (mobile app style)")
        print(f"   URL: {BASE_URL}/ai/advanced-search/")
        print(f"   Method: POST")
        print(f"   Content-Type: multipart/form-data (auto-generated)")
        
        start_time = time.time()
        
        # Make the exact same request as mobile app
        response = requests.post(
            f"{BASE_URL}/ai/advanced-search/",
            files=files,
            data=data,
            timeout=60,  # Same timeout as mobile app
            verify=False,  # Disable SSL verification for testing
            headers={
                # Don't set Content-Type - let requests set it with boundary (same as mobile app)
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Mobile app API call successful!")
            result = response.json()
            
            # Analyze the results exactly like mobile app would
            analyze_mobile_app_results(result, response_time)
            
        else:
            print(f"❌ Mobile app API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error (mobile app simulation): {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error (mobile app simulation): {e}")
        return False
    
    print()
    print("📊 STEP 3: Mobile App Response Processing")
    print("-" * 40)
    
    # Simulate mobile app response processing
    mobile_app_processing(result)
    
    print()
    print("🎯 STEP 4: Mobile App UI State Simulation")
    print("-" * 40)
    
    # Simulate mobile app UI state updates
    simulate_mobile_ui_state(result)
    
    print()
    print("🏁 MOBILE APP SIMULATION COMPLETE")
    print("=" * 50)
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

def analyze_mobile_app_results(result, response_time):
    """Analyze results exactly like the mobile app would."""
    
    print("\n📈 MOBILE APP ANALYSIS RESULTS:")
    print("-" * 35)
    
    # Extract data exactly like mobile app does
    analysis = result.get('analysis', {})
    queries = result.get('queries', {})
    results = result.get('results', [])
    summary = result.get('summary', {})
    
    # Analysis quality (mobile app displays this)
    analysis_quality = summary.get('analysis_quality', 'unknown')
    print(f"📊 Analysis Quality: {analysis_quality.upper()}")
    
    # AI Services Status (mobile app shows these indicators)
    ai_services = analysis
    services = ['vision', 'rekognition', 'gemini', 'vertex']
    print("\n🤖 AI Services Status (Mobile App Display):")
    for service in services:
        if ai_services.get(service):
            print(f"   ✅ {service.upper()}: Active")
        else:
            print(f"   ❌ {service.upper()}: Inactive")
    
    # Confidence scores (mobile app shows these bars)
    confidence_scores = analysis.get('confidence_scores', {})
    if confidence_scores:
        print("\n🎯 Confidence Scores (Mobile App Bars):")
        for service, score in confidence_scores.items():
            status = "🟢" if score > 80 else "🟡" if score > 60 else "🔴"
            print(f"   {status} {service}: {score}%")
    
    # Query variants (mobile app shows these as selectable options)
    query_variants = queries.get('variants', [])
    if query_variants:
        print("\n🔍 Query Variants (Mobile App Selection Options):")
        for i, variant in enumerate(query_variants, 1):
            print(f"   {i}. {variant['query']}")
            print(f"      Source: {variant['source']}")
            print(f"      Confidence: {variant['confidence']}%")
    
    # Primary query (mobile app uses this as default)
    primary_query = queries.get('primary', 'N/A')
    print(f"\n🎯 Primary Query (Mobile App Default): {primary_query}")
    
    # Search results (mobile app displays these in cards)
    print(f"\n📦 Search Results (Mobile App Cards): {len(results)} items found")
    
    if results:
        print("\nTop 3 Results (Mobile App Display):")
        for i, item in enumerate(results[:3], 1):
            title = item.get('title', 'No title')
            if len(title) > 50:
                title = title[:50] + "..."
            
            # Handle price like mobile app does
            price = item.get('price', {})
            if isinstance(price, dict):
                price_value = price.get('value', 'N/A')
            else:
                price_value = price if price else 'N/A'
            
            condition = item.get('condition', 'N/A')
            
            print(f"   {i}. {title}")
            print(f"      Price: ${price_value}")
            print(f"      Condition: {condition}")
    
    # Performance assessment (mobile app shows loading indicators)
    print(f"\n⏱️  Performance (Mobile App Loading):")
    print(f"   Response Time: {response_time:.2f}s")
    if response_time < 5:
        print("   🟢 Excellent (Mobile app would show fast loading)")
    elif response_time < 10:
        print("   🟡 Good (Mobile app would show normal loading)")
    else:
        print("   🔴 Slow (Mobile app would show slow loading indicator)")

def mobile_app_processing(result):
    """Simulate mobile app response processing."""
    
    print("\n📱 MOBILE APP RESPONSE PROCESSING:")
    print("-" * 35)
    
    # Simulate mobile app state updates
    print("🔄 Simulating mobile app state updates...")
    
    # Extract data like mobile app does
    analysis = result.get('analysis', {})
    queries = result.get('queries', {})
    results = result.get('results', [])
    summary = result.get('summary', {})
    
    # Simulate mobile app state variables
    mobile_states = {
        'searchResults': results,
        'analysis': analysis,
        'bestGuess': queries.get('primary', ''),
        'suggestedQueries': [v['query'] for v in queries.get('variants', [])],
        'confidenceScores': analysis.get('confidence_scores', {}),
        'queryVariants': queries.get('variants', []),
        'selectedQueryVariant': queries.get('primary', ''),
        'analysisQuality': summary.get('analysis_quality', 'medium'),
        'aiServicesStatus': {
            'vision': bool(analysis.get('vision')),
            'rekognition': bool(analysis.get('rekognition')),
            'gemini': bool(analysis.get('gemini')),
            'vertex': bool(analysis.get('vertex'))
        }
    }
    
    print("✅ Mobile app state variables updated:")
    for key, value in mobile_states.items():
        if isinstance(value, list):
            print(f"   {key}: {len(value)} items")
        elif isinstance(value, dict):
            print(f"   {key}: {len(value)} keys")
        else:
            print(f"   {key}: {value}")
    
    # Simulate mobile app success alert
    if results:
        print(f"\n📱 Mobile app would show: 'Advanced AI Search Complete - Found {len(results)} items with {summary.get('analysis_quality', 'medium')} quality analysis!'")
    else:
        print(f"\n📱 Mobile app would show: 'No Results - No items found for this image. Try a different photo.'")

def simulate_mobile_ui_state(result):
    """Simulate mobile app UI state and interactions."""
    
    print("\n📱 MOBILE APP UI STATE SIMULATION:")
    print("-" * 35)
    
    # Simulate mobile app UI components
    print("🎨 Simulating mobile app UI components...")
    
    # 1. Image display (mobile app shows selected image)
    print("📸 Image Display: Selected image would be displayed")
    
    # 2. AI Services Status Grid (mobile app shows status indicators)
    ai_services = result.get('analysis', {})
    services = ['vision', 'rekognition', 'gemini', 'vertex']
    print("\n🤖 AI Services Status Grid:")
    for service in services:
        status = "Active" if ai_services.get(service) else "Inactive"
        print(f"   {service.upper()}: {status}")
    
    # 3. Confidence Bars (mobile app shows visual bars)
    confidence_scores = result.get('analysis', {}).get('confidence_scores', {})
    if confidence_scores:
        print("\n📊 Confidence Bars:")
        for service, score in confidence_scores.items():
            bar_length = int(score / 10)  # Simulate visual bar
            bar = "█" * bar_length + "░" * (10 - bar_length)
            print(f"   {service}: [{bar}] {score}%")
    
    # 4. Query Variants (mobile app shows as selectable cards)
    query_variants = result.get('queries', {}).get('variants', [])
    if query_variants:
        print("\n🔍 Query Variant Cards:")
        for i, variant in enumerate(query_variants, 1):
            print(f"   Card {i}: {variant['query']}")
            print(f"      Source: {variant['source']}")
            print(f"      Confidence: {variant['confidence']}%")
    
    # 5. Analysis Quality Indicator (mobile app shows color-coded indicator)
    analysis_quality = result.get('summary', {}).get('analysis_quality', 'medium')
    quality_colors = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}
    quality_color = quality_colors.get(analysis_quality, '⚪')
    print(f"\n📈 Analysis Quality Indicator: {quality_color} {analysis_quality.upper()}")
    
    # 6. Search Results (mobile app shows as cards)
    results = result.get('results', [])
    if results:
        print(f"\n📦 Search Result Cards: {len(results)} items")
        for i, item in enumerate(results[:3], 1):
            title = item.get('title', 'No title')
            if len(title) > 30:
                title = title[:30] + "..."
            print(f"   Card {i}: {title}")
    
    print("\n✅ Mobile app UI state simulation complete!")

if __name__ == "__main__":
    print("🚀 Starting Mobile App Simulation Test")
    print("=" * 60)
    print("This test simulates the exact behavior of the mobile app")
    print("using the test image instead of camera input.")
    print()
    
    success = simulate_mobile_app_search()
    
    if success:
        print("\n🎉 Mobile app simulation completed successfully!")
        print("The AI system is working correctly with the mobile app.")
    else:
        print("\n❌ Mobile app simulation failed!")
        print("Please check the system configuration and try again.")
    
    print("\n" + "=" * 60) 