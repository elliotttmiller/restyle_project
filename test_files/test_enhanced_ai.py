#!/usr/bin/env python3
"""
Comprehensive test for enhanced AI term extraction
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
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image_with_text(text, color='red', size=(200, 200)):
    """Create a test image with text"""
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # Add text to image
    draw.text((10, 10), text, fill='white', font=font)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()

def test_enhanced_ai_term_extraction():
    """Test the enhanced AI term extraction"""
    print("Testing Enhanced AI Term Extraction...")
    
    # Test cases with different scenarios
    test_cases = [
        {
            'name': 'Red Jordan 4',
            'image_data': create_test_image_with_text('Jordan 4', 'red'),
            'expected_terms': ['jordan', 'red', 'sneakers']
        },
        {
            'name': 'Blue Nike Hoodie',
            'image_data': create_test_image_with_text('Nike Hoodie', 'blue'),
            'expected_terms': ['nike', 'blue', 'hoodie']
        },
        {
            'name': 'Green Adidas Shoes',
            'image_data': create_test_image_with_text('Adidas', 'green'),
            'expected_terms': ['adidas', 'green', 'shoes']
        },
        {
            'name': 'Purple Converse',
            'image_data': create_test_image_with_text('Converse Chuck Taylor', 'purple'),
            'expected_terms': ['converse', 'purple', 'sneakers']
        },
        {
            'name': 'Generic Clothing',
            'image_data': create_test_image_with_text('Clothing', 'gray'),
            'expected_terms': ['clothing']
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        
        try:
            # Test AI analysis
            results = ai_service.analyze_image(test_case['image_data'])
            search_terms = results.get('search_terms', [])
            
            print(f"  Generated terms: {search_terms}")
            print(f"  Expected terms: {test_case['expected_terms']}")
            
            # Check if we have meaningful terms
            if len(search_terms) >= 1:
                print(f"  ✅ Generated {len(search_terms)} terms")
                
                # Check for brand detection
                brands = ['jordan', 'nike', 'adidas', 'converse', 'puma', 'reebok']
                detected_brands = [term for term in search_terms if term.lower() in brands]
                if detected_brands:
                    print(f"  🏷️  Detected brands: {detected_brands}")
                
                # Check for color detection
                colors = ['red', 'blue', 'green', 'purple', 'yellow', 'orange', 'pink', 'brown', 'navy', 'maroon', 'olive', 'teal']
                detected_colors = [term for term in search_terms if term.lower() in colors]
                if detected_colors:
                    print(f"  🎨 Detected colors: {detected_colors}")
                
                # Check for product types
                products = ['shoes', 'sneakers', 'hoodie', 'shirt', 'pants', 'jeans', 'dress', 'jacket']
                detected_products = [term for term in search_terms if term.lower() in products]
                if detected_products:
                    print(f"  👕 Detected products: {detected_products}")
                
            else:
                print(f"  ⚠️  No meaningful terms generated")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_color_detection():
    """Test color detection specifically"""
    print("\n--- Testing Color Detection ---")
    
    colors_to_test = ['red', 'blue', 'green', 'yellow', 'purple', 'pink', 'orange', 'brown', 'navy', 'maroon']
    
    for color in colors_to_test:
        print(f"\nTesting {color} color...")
        
        # Create image with specific color
        img = Image.new('RGB', (100, 100), color=color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        image_data = img_bytes.getvalue()
        
        try:
            results = ai_service.analyze_image(image_data)
            search_terms = results.get('search_terms', [])
            
            if color in search_terms:
                print(f"  ✅ Correctly detected {color}")
            else:
                print(f"  ❌ Failed to detect {color}")
                print(f"     Generated terms: {search_terms}")
                
        except Exception as e:
            print(f"  ❌ Error testing {color}: {e}")

def test_brand_detection():
    """Test brand detection from OCR"""
    print("\n--- Testing Brand Detection ---")
    
    brands_to_test = [
        ('Jordan 4', ['jordan']),
        ('Nike Air Max', ['nike']),
        ('Adidas Ultraboost', ['adidas']),
        ('Converse Chuck Taylor', ['converse']),
        ('Vans Old Skool', ['vans'])
    ]
    
    for brand_text, expected_brands in brands_to_test:
        print(f"\nTesting brand text: '{brand_text}'")
        
        # Create image with brand text
        image_data = create_test_image_with_text(brand_text, 'white')
        
        try:
            results = ai_service.analyze_image(image_data)
            search_terms = results.get('search_terms', [])
            
            detected_brands = [term for term in search_terms if term.lower() in expected_brands]
            if detected_brands:
                print(f"  ✅ Detected brands: {detected_brands}")
            else:
                print(f"  ❌ Failed to detect brands from '{brand_text}'")
                print(f"     Generated terms: {search_terms}")
                
        except Exception as e:
            print(f"  ❌ Error testing '{brand_text}': {e}")

def test_current_ai_system():
    """Test the current AI system with the available setup"""
    print("\n🧪 Testing Current AI System Setup...")
    
    # Create a simple test image (1x1 pixel)
    test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf5\x8d\xb4\x1d\x00\x00\x00\x00IEND\xaeB`\x82'
    
    try:
        # Initialize AI service
        ai_service = AIService()
        
        # Test basic analysis
        results = ai_service.analyze_image(test_image_data)
        
        print(f"✅ AI Service initialized successfully")
        print(f"   - Google Cloud Vision available: {ai_service.client is not None}")
        print(f"   - Generated search terms: {results.get('search_terms', [])}")
        print(f"   - Labels detected: {[label['description'] for label in results.get('labels', [])]}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Service test failed: {e}")
        return False

if __name__ == "__main__":
    # Run the current system test first
    test_current_ai_system()
    
    # Then run the comprehensive tests
    test_enhanced_ai_term_extraction()
    
    # Test color detection
    test_color_detection()
    
    # Test brand detection
    test_brand_detection()
    
    print("\n✅ All tests completed!") 