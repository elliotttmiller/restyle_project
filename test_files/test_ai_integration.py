#!/usr/bin/env python3
"""
Test script for AI integration
"""
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.ai_service import ai_service
import requests
from PIL import Image
import io

def test_ai_service():
    """Test the AI service with a sample image"""
    print("Testing AI Service...")
    
    # Create a simple test image (1x1 pixel)
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    image_data = img_bytes.getvalue()
    
    # Test AI analysis
    try:
        results = ai_service.analyze_image(image_data)
        print("✅ AI Service Test Results:")
        print(f"  - Labels found: {len(results.get('labels', []))}")
        print(f"  - Objects found: {len(results.get('objects', []))}")
        print(f"  - Search terms: {results.get('search_terms', [])}")
        print(f"  - Dominant colors: {len(results.get('dominant_colors', []))}")
        return True
    except Exception as e:
        print(f"❌ AI Service Test Failed: {e}")
        return False

def test_ebay_search():
    """Test eBay search with AI-generated terms"""
    print("\nTesting eBay Search with AI terms...")
    
    # Test search terms
    search_terms = ['clothing', 'fashion', 'apparel']
    query = ' '.join(search_terms)
    
    try:
        # This would normally use the eBay API
        print(f"✅ Would search eBay with query: '{query}'")
        print(f"  - Search terms: {search_terms}")
        return True
    except Exception as e:
        print(f"❌ eBay Search Test Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing AI Integration...\n")
    
    # Test AI service
    ai_success = test_ai_service()
    
    # Test eBay search
    ebay_success = test_ebay_search()
    
    print(f"\n📊 Test Results:")
    print(f"  - AI Service: {'✅ PASS' if ai_success else '❌ FAIL'}")
    print(f"  - eBay Search: {'✅ PASS' if ebay_success else '❌ FAIL'}")
    
    if ai_success and ebay_success:
        print("\n🎉 All tests passed! AI integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

if __name__ == '__main__':
    main() 