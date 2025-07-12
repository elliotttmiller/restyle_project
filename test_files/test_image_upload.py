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
username = os.environ.get('DJANGO_TEST_USER', 'admin')
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
    """Analyze AI system results and display real eBay search results"""
    print("\n" + "="*80)
    print("🤖 AI-DRIVEN SEARCH RESULTS ANALYSIS")
    print("="*80)
    
    # Extract key information
    search_terms = response_data.get('search_terms', [])
    visual_results = response_data.get('visual_search_results', [])
    hybrid_results = response_data.get('hybrid_results', [])
    
    print(f"\n📊 AI SYSTEM SUMMARY:")
    print(f"   • Image: {os.path.basename(IMAGE_PATH)}")
    print(f"   • Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   • AI-Detected Search Terms: {len(search_terms)}")
    print(f"   • Visual Search Results: {len(visual_results)}")
    print(f"   • Hybrid Search Results: {len(hybrid_results)}")
    
    # Display AI-detected search terms
    print(f"\n🔍 AI-DETECTED SEARCH TERMS:")
    for i, term in enumerate(search_terms, 1):
        print(f"   {i}. '{term}'")
    
    # Display search queries used
    search_queries = response_data.get('search_queries_used', {})
    print(f"\n🔍 AI-GENERATED SEARCH QUERIES:")
    print(f"   Primary Query: {search_queries.get('primary_query', 'None')}")
    print(f"   Suggested Queries Tried: {search_queries.get('suggested_queries_tried', [])}")
    
    # Display eBay search results
    ebay_results = response_data.get('ebay_search_results', [])
    print(f"\n🛒 EBAY SEARCH RESULTS (AI-GENERATED QUERY):")
    print(f"   Total eBay Items Found: {len(ebay_results)}")
    
    if ebay_results:
        print("   Top 10 eBay Items:")
        for i, item in enumerate(ebay_results[:10], 1):
            title = item.get('title', 'No title')
            price = item.get('price', {}).get('value', 'No price')
            url = item.get('itemWebUrl', 'No URL')
            print(f"   {i}. {title}")
            print(f"      Price: ${price}")
            print(f"      URL: {url}")
            print()
    else:
        print("   ❌ No eBay items found")
    
    # Display visual search results
    if visual_results:
        print(f"\n👁️ VISUAL SEARCH RESULTS:")
        print(f"   Total Visual Results: {len(visual_results)}")
        print("   Top 5 Visual Results:")
        for i, result in enumerate(visual_results[:5], 1):
            title = result.get('title', 'No title')
            url = result.get('url', 'No URL')
            print(f"   {i}. {title}")
            print(f"      URL: {url}")
    
    # Display hybrid results
    if hybrid_results:
        print(f"\n🔄 HYBRID SEARCH RESULTS:")
        print(f"   Total Hybrid Results: {len(hybrid_results)}")
        print("   Top 5 Hybrid Results:")
        for i, result in enumerate(hybrid_results[:5], 1):
            title = result.get('title', 'No title')
            url = result.get('url', 'No URL')
            print(f"   {i}. {title}")
            print(f"      URL: {url}")
    
    # AI System Assessment
    print(f"\n🎯 AI SYSTEM ASSESSMENT:")
    print(f"   • Search Terms Detected: {len(search_terms)}")
    print(f"   • eBay Items Found: {len(ebay_results)}")
    print(f"   • Visual Results: {len(visual_results)}")
    print(f"   • Hybrid Results: {len(hybrid_results)}")
    
    if len(ebay_results) > 0:
        print(f"   ✅ SUCCESS: AI system found {len(ebay_results)} relevant eBay items")
    else:
        print(f"   ❌ NO RESULTS: AI system found no eBay items")
    
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
            response = requests.post(API_URL, headers=headers, files=files, timeout=120)
            
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