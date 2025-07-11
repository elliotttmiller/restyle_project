#!/usr/bin/env python3
"""
Enhanced test script to analyze AI system accuracy
"""
import requests
import os
import json
from datetime import datetime

API_URL = 'http://localhost:8000/api/core/ai/image-search/'
# Use absolute path for the new test image
IMAGE_PATH = r'C:\Users\AMD\restyle_project\test_files\example2.JPG'
AUTH_URL = 'http://localhost:8000/api/token/'

# Use environment variables or defaults for test credentials
username = os.environ.get('DJANGO_TEST_USER', 'testuser')
password = os.environ.get('DJANGO_TEST_PASS', 'elliott123')

def get_jwt_token():
    auth_data = {
        'username': username,
        'password': password
    }
    try:
        response = requests.post(AUTH_URL, json=auth_data, timeout=10)
        if response.status_code == 200:
            token = response.json().get('access')
            if token:
                print('✅ Authenticated, got JWT token')
                return token
            else:
                print('❌ No access token in response')
        else:
            print(f'❌ Authentication failed: {response.status_code}')
            print('Response:', response.text)
    except Exception as e:
        print(f'❌ Error during authentication: {e}')
    return None

def analyze_ai_results(response_data):
    """Analyze AI system accuracy and provide detailed feedback"""
    print("\n" + "="*80)
    print("🤖 AI SYSTEM ACCURACY ANALYSIS")
    print("="*80)
    
    # Extract key information
    search_terms = response_data.get('search_terms', [])
    visual_results = response_data.get('visual_search_results', [])
    hybrid_results = response_data.get('hybrid_results', [])
    
    print(f"\n📊 TEST SUMMARY:")
    print(f"   • Image: {os.path.basename(IMAGE_PATH)}")
    print(f"   • Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   • Search Terms Generated: {len(search_terms)}")
    print(f"   • Visual Results: {len(visual_results)}")
    print(f"   • Hybrid Results: {len(hybrid_results)}")
    
    # Analyze search terms
    print(f"\n🔍 AI DETECTED SEARCH TERMS:")
    for i, term in enumerate(search_terms, 1):
        print(f"   {i}. '{term}'")
    
    # Analyze visual results
    if visual_results:
        print(f"\n👁️ TOP VISUAL SEARCH RESULTS:")
        for i, result in enumerate(visual_results[:5], 1):
            title = result.get('title', 'No title')
            url = result.get('url', 'No URL')
            print(f"   {i}. {title}")
            print(f"      URL: {url}")
    
    # Analyze hybrid results
    if hybrid_results:
        print(f"\n🔄 TOP HYBRID SEARCH RESULTS:")
        for i, result in enumerate(hybrid_results[:5], 1):
            title = result.get('title', 'No title')
            url = result.get('url', 'No URL')
            print(f"   {i}. {title}")
            print(f"      URL: {url}")
    
    # Accuracy assessment
    print(f"\n📈 ACCURACY ASSESSMENT:")
    
    # Check for expected terms in search results
    expected_terms = ['burberry', 'shirt', 'long sleeve', 'button', 'beige', 'thornaby']
    detected_terms = [term.lower() for term in search_terms]
    
    print(f"   Expected Terms: {expected_terms}")
    print(f"   Detected Terms: {detected_terms}")
    
    # Calculate accuracy metrics
    correct_detections = sum(1 for term in expected_terms if any(term in detected for detected in detected_terms))
    accuracy_percentage = (correct_detections / len(expected_terms)) * 100 if expected_terms else 0
    
    print(f"   Correct Detections: {correct_detections}/{len(expected_terms)}")
    print(f"   Accuracy: {accuracy_percentage:.1f}%")
    
    # Specific accuracy checks
    print(f"\n✅ SPECIFIC ACCURACY CHECKS:")
    
    # Brand detection
    brand_detected = any('burberry' in term.lower() for term in search_terms)
    print(f"   • Brand (Burberry): {'✅' if brand_detected else '❌'}")
    
    # Product type detection
    shirt_detected = any('shirt' in term.lower() for term in search_terms)
    print(f"   • Product Type (Shirt): {'✅' if shirt_detected else '❌'}")
    
    # Color detection
    color_detected = any(color in ' '.join(search_terms).lower() for color in ['beige', 'tan', 'cream', 'light brown'])
    print(f"   • Color (Beige/Tan): {'✅' if color_detected else '❌'}")
    
    # Style detection
    style_detected = any(style in ' '.join(search_terms).lower() for style in ['long sleeve', 'button', 'formal'])
    print(f"   • Style (Long Sleeve/Button): {'✅' if style_detected else '❌'}")
    
    # Model detection
    model_detected = any('thornaby' in term.lower() for term in search_terms)
    print(f"   • Model (Thornaby): {'✅' if model_detected else '❌'}")
    
    # Overall assessment
    print(f"\n🎯 OVERALL ASSESSMENT:")
    if accuracy_percentage >= 80:
        print("   🟢 EXCELLENT: AI system is highly accurate")
    elif accuracy_percentage >= 60:
        print("   🟡 GOOD: AI system is performing well")
    elif accuracy_percentage >= 40:
        print("   🟠 FAIR: AI system needs improvement")
    else:
        print("   🔴 POOR: AI system needs significant improvement")
    
    print("="*80)

def main():
    print("🚀 STARTING AI SYSTEM ACCURACY TEST")
    print(f"📁 Testing image: {os.path.basename(IMAGE_PATH)}")
    
    token = get_jwt_token()
    if not token:
        print('❌ Could not get JWT token, aborting image upload test.')
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
    }
    
    try:
        with open(IMAGE_PATH, 'rb') as image_file:
            files = {
                'image': image_file,
            }
            print("\n📤 Uploading image to AI system...")
            response = requests.post(API_URL, headers=headers, files=files, timeout=30)
            
            print(f'Status code: {response.status_code}')
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    analyze_ai_results(response_data)
                except Exception as e:
                    print(f'❌ Error parsing response: {e}')
                    print('Raw response:', response.text)
            else:
                print(f'❌ Request failed with status {response.status_code}')
                print('Response:', response.text)
                
    except Exception as e:
        print(f'❌ Error during image upload: {e}')

if __name__ == '__main__':
    main() 