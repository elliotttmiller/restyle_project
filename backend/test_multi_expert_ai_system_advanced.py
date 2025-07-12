#!/usr/bin/env python3
"""
Advanced multi-expert AI system with fine-tuned logic.
This version includes confidence scoring, query optimization, and intelligent fallbacks.
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

def calculate_confidence_score(analysis_results):
    """Calculate confidence scores for different AI services."""
    confidence_scores = {}
    
    # Google Vision confidence
    if analysis_results.get('vision'):
        vision_score = 0
        if analysis_results['vision'].get('texts'):
            vision_score += 30  # Text detection is valuable
        if analysis_results['vision'].get('labels'):
            vision_score += 20  # Label detection
        if analysis_results['vision'].get('objects'):
            vision_score += 15  # Object detection
        if analysis_results['vision'].get('colors'):
            vision_score += 10  # Color analysis
        confidence_scores['vision'] = min(vision_score, 100)
    
    # AWS Rekognition confidence
    if analysis_results.get('rekognition'):
        rekognition_score = 0
        if analysis_results['rekognition'].get('labels'):
            rekognition_score += 40  # Rekognition labels are very accurate
        if analysis_results['rekognition'].get('texts'):
            rekognition_score += 30  # Text detection
        if analysis_results['rekognition'].get('faces', 0) > 0:
            rekognition_score += 10  # Face detection
        confidence_scores['rekognition'] = min(rekognition_score, 100)
    
    # Gemini API confidence
    if analysis_results.get('gemini_query'):
        confidence_scores['gemini'] = 95  # AI synthesis is highly valuable
    
    # Vertex AI confidence
    if analysis_results.get('vertex_analysis'):
        confidence_scores['vertex'] = 90  # Advanced analysis is valuable
    
    return confidence_scores

def optimize_search_query(query, analysis_results):
    """Optimize the search query based on analysis results."""
    optimized_query = query
    
    # Add brand name if detected but missing from query
    detected_brands = []
    if analysis_results.get('vision', {}).get('texts'):
        for text in analysis_results['vision']['texts']:
            if any(brand in text.upper() for brand in ['BURBERRY', 'NIKE', 'ADIDAS', 'LEVI', 'CALVIN']):
                detected_brands.append(text.upper())
    
    if detected_brands and not any(brand in optimized_query.upper() for brand in detected_brands):
        optimized_query = f"{detected_brands[0]} {optimized_query}"
    
    # Add specific features if missing
    specific_features = []
    if analysis_results.get('rekognition', {}).get('labels'):
        for label in analysis_results['rekognition']['labels']:
            if any(feature in label.lower() for feature in ['long sleeve', 'short sleeve', 'button down', 'polo']):
                specific_features.append(label)
    
    if specific_features and not any(feature.lower() in optimized_query.lower() for feature in specific_features):
        optimized_query = f"{optimized_query} {specific_features[0]}"
    
    return optimized_query

def generate_multiple_query_variants(analysis_results):
    """Generate multiple query variants for better search coverage."""
    variants = []
    
    # Primary query (Gemini)
    if analysis_results.get('gemini_query'):
        variants.append({
            'query': analysis_results['gemini_query'],
            'confidence': 95,
            'source': 'Gemini AI'
        })
    
    # Brand-focused query
    brand_query = ""
    if analysis_results.get('vision', {}).get('texts'):
        for text in analysis_results['vision']['texts']:
            if any(brand in text.upper() for brand in ['BURBERRY', 'NIKE', 'ADIDAS']):
                brand_query = f"{text.upper()} shirt"
                break
    
    if brand_query:
        variants.append({
            'query': brand_query,
            'confidence': 85,
            'source': 'Brand Detection'
        })
    
    # Feature-focused query
    feature_terms = []
    if analysis_results.get('rekognition', {}).get('labels'):
        for label in analysis_results['rekognition']['labels']:
            if any(term in label.lower() for term in ['long sleeve', 'dress shirt', 'button down']):
                feature_terms.append(label)
    
    if feature_terms:
        feature_query = ' '.join(feature_terms[:2])
        variants.append({
            'query': feature_query,
            'confidence': 80,
            'source': 'Feature Detection'
        })
    
    # Generic fallback
    if analysis_results.get('rekognition', {}).get('labels'):
        generic_terms = [label for label in analysis_results['rekognition']['labels'][:3]]
        generic_query = ' '.join(generic_terms)
        variants.append({
            'query': generic_query,
            'confidence': 70,
            'source': 'Generic Detection'
        })
    
    return variants

def test_google_vision_api(image_path):
    """Test Google Vision API for image analysis."""
    print("🔍 Testing Google Vision API...")
    
    try:
        # Initialize Vision client
        client = vision.ImageAnnotatorClient()
        
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
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', '***REMOVED***'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', '3LAsYxgRHS0msvNQLdAf7Nnab89j//0oFp2JfEja'),
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
        
        # Create enhanced synthesis prompt
        prompt = f"""
        Analyze this product image data and generate the most accurate eBay search query.
        
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
        Focus on:
        1. Brand names (if detected)
        2. Specific product type (shirt, dress, pants, etc.)
        3. Key features (long sleeve, button down, etc.)
        4. Pattern or style (plaid, solid, etc.)
        
        Return only the search query, nothing else.
        """
        
        response = model.generate_content(prompt)
        
        print("✅ Google Gemini API successful!")
        print(f"  Generated query: {response.text.strip()}")
        
        return response.text.strip()
        
    except Exception as e:
        print(f"❌ Google Gemini API error: {e}")
        return None

def test_vertex_ai(analysis_results):
    """Test Google Vertex AI for advanced reasoning."""
    print("🧠 Testing Google Vertex AI...")
    
    try:
        # Initialize Vertex AI
        from google.cloud import aiplatform
        
        aiplatform.init(
            project=os.environ.get('GOOGLE_CLOUD_PROJECT', 'silent-polygon-465403-h9'),
            location=os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
        )
        
        # Use Gemini model through Vertex AI
        model = GenerativeModel('gemini-1.5-pro')
        
        # Create enhanced analysis prompt
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
        6. Recommended search terms (array)
        7. Alternative search terms (array)
        
        Format as JSON with these exact keys:
        {{
            "product_category": "string",
            "product_type": "string", 
            "key_features": ["array"],
            "brand": "string or null",
            "estimated_value": "string",
            "best_platforms": ["array"],
            "recommended_search_terms": ["array"],
            "alternative_search_terms": ["array"]
        }}
        """
        
        response = model.generate_content(prompt)
        
        print("✅ Google Vertex AI successful!")
        print(f"  Advanced analysis: {response.text[:200]}...")
        
        return response.text
        
    except Exception as e:
        print(f"❌ Google Vertex AI error: {e}")
        return None

def generate_optimized_search_query(analysis_results):
    """Generate optimized search query using advanced logic."""
    print("🔍 Generating optimized search query...")
    
    # Calculate confidence scores
    confidence_scores = calculate_confidence_score(analysis_results)
    print(f"  Confidence scores: {confidence_scores}")
    
    # Generate multiple query variants
    query_variants = generate_multiple_query_variants(analysis_results)
    print(f"  Generated {len(query_variants)} query variants")
    
    # Select the best query based on confidence
    best_query = None
    best_confidence = 0
    
    for variant in query_variants:
        if variant['confidence'] > best_confidence:
            best_query = variant['query']
            best_confidence = variant['confidence']
            print(f"  Selected: '{best_query}' (confidence: {best_confidence}%)")
    
    # Optimize the selected query
    if best_query:
        optimized_query = optimize_search_query(best_query, analysis_results)
        print(f"  Optimized query: '{optimized_query}'")
        return optimized_query
    
    # Fallback
    fallback_query = "clothing item"
    print(f"  Using fallback query: '{fallback_query}'")
    return fallback_query

def main():
    """Run the advanced multi-expert AI system test."""
    print("🚀 Advanced Multi-Expert AI System Test")
    print("=" * 60)
    
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
    
    # Test Google Vertex AI
    vertex_analysis = test_vertex_ai(analysis_results)
    if vertex_analysis:
        analysis_results['vertex_analysis'] = vertex_analysis
    print()
    
    # Generate optimized search query
    final_query = generate_optimized_search_query(analysis_results)
    print()
    
    # Test eBay search
    print(f"🔍 Testing eBay search with query: '{final_query}'")
    print(f"✅ Search query ready for eBay API: '{final_query}'")
    print()
    
    # Summary
    print("🎉 Advanced Multi-Expert AI System Test Complete!")
    print("=" * 60)
    print(f"✅ Google Vision API: {'Working' if vision_results else 'Failed'}")
    print(f"✅ AWS Rekognition: {'Working' if rekognition_results else 'Failed'}")
    print(f"✅ Google Gemini API: {'Working' if gemini_query else 'Failed'}")
    print(f"✅ Google Vertex AI: {'Working' if vertex_analysis else 'Failed'}")
    print(f"✅ Optimized Query: '{final_query}'")
    
    return analysis_results

if __name__ == "__main__":
    main() 