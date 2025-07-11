#!/usr/bin/env python3
"""
Test script for AI search terms generation
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
from PIL import Image
import io

def test_search_terms():
    """Test the search terms generation"""
    print("Testing AI Search Terms Generation...")
    
    # Create test images with different characteristics
    test_cases = [
        ("Red clothing", (100, 100), 'red'),
        ("Blue clothing", (100, 100), 'blue'),
        ("Green clothing", (100, 100), 'green'),
        ("Black clothing", (100, 100), 'black'),
    ]
    
    for test_name, size, color in test_cases:
        print(f"\n--- Testing: {test_name} ---")
        
        # Create test image
        img = Image.new('RGB', size, color=color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        image_data = img_bytes.getvalue()
        
        # Test AI analysis
        try:
            results = ai_service.analyze_image(image_data)
            search_terms = results.get('search_terms', [])
            query = ' '.join(search_terms[:3])  # Limit to top 3 terms
            
            print(f"  Search terms: {search_terms}")
            print(f"  Final query: '{query}'")
            print(f"  Query length: {len(query)} characters")
            
            if len(query) > 100:
                print(f"  ⚠️  WARNING: Query too long ({len(query)} chars)")
            elif len(query) < 5:
                print(f"  ⚠️  WARNING: Query too short ({len(query)} chars)")
            else:
                print(f"  ✅ Query length looks good")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def main():
    """Run the test"""
    print("🧪 Testing AI Search Terms Generation...\n")
    test_search_terms()
    print("\n✅ Test completed!")

if __name__ == '__main__':
    main() 