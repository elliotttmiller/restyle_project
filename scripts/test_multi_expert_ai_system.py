#!/usr/bin/env python3
"""
Comprehensive test of the multi-expert AI system.
This script tests all AI services working together to generate accurate eBay search queries.
"""

import os
import sys
import json
import boto3
import requests
from google.cloud import vision
from google.generativeai import GenerativeModel
import google.generativeai as genai
from botocore.exceptions import ClientError, NoCredentialsError

def test_google_vision_api(image_path):
    """Test Google Vision API for image analysis."""
    print("🔍 Testing Google Vision API...")
    
    try:
        # Initialize Vision client with API key
        google_api_key = os.environ.get('GOOGLE_API_KEY')
        if not google_api_key:
            print("❌ No GOOGLE_API_KEY found")
            return False
            
        client_options = {"api_key": google_api_key}
        client = vision.ImageAnnotatorClient(client_options=client_options)
        
        # Read image
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        # Perform multiple analyses
        response = client.annotate_image({
            'image': image,
            'features': [
                {'type_': vision.Feature.Type.LABEL_DETECTION},
                {'type_': vision.Feature.Type.TEXT_DETECTION},
                {'type_': vision.Feature.Type.OBJECT_LOCALIZATION},
                {'type_': vision.Feature.Type.IMAGE_PROPERTIES}
            ]
        })
        
        # Extract results
        labels = [label.description for label in response.label_annotations]
        texts = [text.description for text in response.text_annotations[1:]]  # Skip first (full image)
        objects = [obj.name for obj in response.localized_object_annotations]
        colors = response.image_properties_annotation.dominant_colors.colors[:5]
        
        print("✅ Google Vision API successful!")
        print(f"  Labels: {labels[:5]}")
        print(f"  Text: {texts[:3]}")
        print(f"  Objects: {objects[:5]}")
        print(f"  Colors: {[f'{c.color.red},{c.color.green},{c.color.blue}' for c in colors]}")
        
        return {
            'labels': labels,
            'texts': texts,
            'objects': objects,
            'colors': colors
        }
        
    except Exception as e:
        print(f"❌ Google Vision API error: {e}")
        return None

def test_aws_rekognition(image_path):
    """Test AWS Rekognition for detailed image analysis."""
    print("🔍 Testing AWS Rekognition...")
    
    try:
        # Initialize Rekognition client
        rekognition = boto3.client(
            'rekognition',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'REDACTED'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'REDACTED'),
            region_name=os.environ.get('AWS_REGION_NAME', 'us-east-1')
        )
        
        # Read image
        with open(image_path, 'rb') as image:
            image_bytes = image.read()
        
        # Perform multiple analyses
        label_response = rekognition.detect_labels(
            Image={'Bytes': image_bytes},
            MaxLabels=10
        )
        
        text_response = rekognition.detect_text(
            Image={'Bytes': image_bytes}
        )
        
        face_response = rekognition.detect_faces(
            Image={'Bytes': image_bytes}
        )
        
        # Extract results
        labels = [label['Name'] for label in label_response['Labels']]
        texts = [text['DetectedText'] for text in text_response['TextDetections']]
        faces = len(face_response['FaceDetails'])
        
        print("✅ AWS Rekognition successful!")
        print(f"  Labels: {labels[:5]}")
        print(f"  Text: {texts[:3]}")
        print(f"  Faces detected: {faces}")
        
        return {
            'labels': labels,
            'texts': texts,
            'faces': faces
        }
        
    except Exception as e:
        print(f"❌ AWS Rekognition error: {e}")
        return None

def test_gemini_api(analysis_results):
    """Test Google Gemini API for intelligent synthesis."""
    print("🧠 Testing Google Gemini API...")
    
    try:
        # Initialize Gemini
        genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
        model = GenerativeModel('gemini-1.5-pro')
        
        # Create synthesis prompt
        prompt = f"""
        Analyze this product image data and generate an accurate eBay search query.
        
        Google Vision Analysis:
        - Labels: {analysis_results.get('vision', {}).get('labels', [])}
        - Text: {analysis_results.get('vision', {}).get('texts', [])}
        - Objects: {analysis_results.get('vision', {}).get('objects', [])}
        - Colors: {analysis_results.get('vision', {}).get('colors', [])}
        
        AWS Rekognition Analysis:
        - Labels: {analysis_results.get('rekognition', {}).get('labels', [])}
        - Text: {analysis_results.get('rekognition', {}).get('texts', [])}
        - Faces: {analysis_results.get('rekognition', {}).get('faces', 0)}
        
        Generate a precise eBay search query that would find this exact product.
        Focus on the most distinctive features and brand names if detected.
        Return only the search query, nothing else.
        """
        
        response = model.generate_content(prompt)
        
        print("✅ Google Gemini API successful!")
        print(f"  Generated query: {response.text.strip()}")
        
        return response.text.strip()
        
    except Exception as e:
        print(f"❌ Google Gemini API error: {e}")
        return None

def test_gemini_ai(analysis_results):
    """Test Google Gemini AI for advanced reasoning."""
    print("🧠 Testing Google Gemini AI...")
    
    try:
        # Initialize Gemini AI
        import google.generativeai as genai
        
        gemini_api_key = os.environ.get('GOOGLE_API_KEY')
        if not gemini_api_key:
            print("❌ No GOOGLE_API_KEY found for Gemini")
            return None
            
        genai.configure(api_key=gemini_api_key)
        from google.generativeai import GenerativeModel
        model = GenerativeModel('gemini-1.5-pro')
        
        # Create advanced analysis prompt
        prompt = f"""
        Perform advanced product analysis for reselling purposes.
        
        Image Analysis Results:
        Vision Labels: {analysis_results.get('vision', {}).get('labels', [])}
        Rekognition Labels: {analysis_results.get('rekognition', {}).get('labels', [])}
        Detected Text: {analysis_results.get('vision', {}).get('texts', []) + analysis_results.get('rekognition', {}).get('texts', [])}
        
        Provide a detailed analysis including:
        1. Product category and type
        2. Key identifying features
        3. Potential brand (if detected)
        4. Estimated value range
        5. Best selling platforms
        6. Recommended search terms
        
        Format as JSON.
        """
        
        response = model.generate_content(prompt)
        
        print("✅ Google Gemini AI successful!")
        print(f"  Advanced analysis: {response.text[:200]}...")
        
        return response.text
        
    except Exception as e:
        print(f"❌ Google Gemini AI error: {e}")
        return None

def generate_ebay_search_query(analysis_results):
    """Generate the final eBay search query using all AI insights."""
    print("🔍 Generating final eBay search query...")
    
    # Priority 1: Use Gemini's intelligent query if available
    if analysis_results.get('gemini_query'):
        final_query = analysis_results['gemini_query']
        print(f"✅ Using Gemini's intelligent query: '{final_query}'")
        return final_query
    
    # Priority 2: Use Gemini AI analysis if available
    if analysis_results.get('gemini_analysis'):
        # Extract search terms from Gemini AI JSON response
        try:
            import json
            gemini_data = json.loads(analysis_results['gemini_analysis'])
            if 'recommended_search_terms' in gemini_data:
                final_query = ' '.join(gemini_data['recommended_search_terms'][:3])
                print(f"✅ Using Gemini AI search terms: '{final_query}'")
                return final_query
        except:
            pass
    
    # Priority 3: Fallback to manual algorithm
    all_labels = set()
    all_texts = set()
    
    # Add Vision labels
    if analysis_results.get('vision'):
        all_labels.update(analysis_results['vision'].get('labels', []))
        all_texts.update(analysis_results['vision'].get('texts', []))
    
    # Add Rekognition labels
    if analysis_results.get('rekognition'):
        all_labels.update(analysis_results['rekognition'].get('labels', []))
        all_texts.update(analysis_results['rekognition'].get('texts', []))
    
    # Create search query
    search_terms = []
    
    # Add brand names from text (including BURBERRY)
    brand_keywords = ['nike', 'adidas', 'puma', 'reebok', 'under armour', 'levi', 'calvin klein', 'tommy hilfiger', 'burberry']
    for text in all_texts:
        text_lower = text.lower()
        for brand in brand_keywords:
            if brand in text_lower:
                search_terms.append(brand.title())
                break
    
    # Add key product terms
    clothing_terms = ['shirt', 'dress', 'pants', 'jeans', 'jacket', 'coat', 'blouse', 'sweater']
    for label in all_labels:
        label_lower = label.lower()
        if any(term in label_lower for term in clothing_terms):
            search_terms.append(label)
            break
    
    # Add specific features
    feature_terms = ['long sleeve', 'short sleeve', 'button down', 'polo', 't-shirt']
    for label in all_labels:
        label_lower = label.lower()
        if any(term in label_lower for term in feature_terms):
            search_terms.append(label)
            break
    
    # Create final query
    if search_terms:
        final_query = ' '.join(search_terms[:3])  # Use top 3 terms
    else:
        # Fallback to most common labels
        final_query = ' '.join(list(all_labels)[:3])
    
    print(f"✅ Generated fallback search query: '{final_query}'")
    return final_query

def test_ebay_search(query):
    """Test the generated query with eBay API (if available)."""
    print(f"🔍 Testing eBay search with query: '{query}'")
    
    # This would integrate with your existing eBay API
    # For now, just show the query
    print(f"✅ Search query ready for eBay API: '{query}'")
    return query

def main():
    """Run the complete multi-expert AI system test."""
    print("🚀 Multi-Expert AI System Test")
    print("=" * 50)
    
    # Test image path
    image_path = r'C:\Users\AMD\restyle_project\test_files\example2.JPG'
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        return
    
    print(f"📸 Analyzing image: {image_path}")
    print()
    
    # Initialize results
    analysis_results = {}
    
    # Test Google Vision API
    vision_results = test_google_vision_api(image_path)
    if vision_results:
        analysis_results['vision'] = vision_results
    print()
    
    # Test AWS Rekognition
    rekognition_results = test_aws_rekognition(image_path)
    if rekognition_results:
        analysis_results['rekognition'] = rekognition_results
    print()
    
    # Test Google Gemini API
    gemini_query = test_gemini_api(analysis_results)
    if gemini_query:
        analysis_results['gemini_query'] = gemini_query
    print()
    
    # Test Google Gemini AI
    gemini_analysis = test_gemini_ai(analysis_results)
    if gemini_analysis:
        analysis_results['gemini_analysis'] = gemini_analysis
    print()
    
    # Generate final eBay search query
    final_query = generate_ebay_search_query(analysis_results)
    print()
    
    # Test eBay search
    test_ebay_search(final_query)
    print()
    
    # Summary
    print("🎉 Multi-Expert AI System Test Complete!")
    print("=" * 50)
    print(f"✅ Google Vision API: {'Working' if vision_results else 'Failed'}")
    print(f"✅ AWS Rekognition: {'Working' if rekognition_results else 'Failed'}")
    print(f"✅ Google Gemini API: {'Working' if gemini_query else 'Failed'}")
    print(f"✅ Google Gemini AI: {'Working' if gemini_analysis else 'Failed'}")
    print(f"✅ Final eBay Query: '{final_query}'")
    
    return analysis_results

if __name__ == "__main__":
    main() 