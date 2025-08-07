#!/usr/bin/env python3
"""
Test script for the new Multi-Expert AI system with Amazon Rekognition and Google Gemini.
This script validates the complete pipeline from image analysis to market search.
"""
import os
import sys
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Get Railway domain from environment
RAILWAY_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN', 'restyleproject-production.up.railway.app')
BASE_URL = f"https://{RAILWAY_DOMAIN}"
credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if credentials_path and os.path.exists(credentials_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    print(f"✅ Google Cloud credentials found at: {credentials_path}")
else:
    print(f"❌ Google Cloud credentials not found at: {credentials_path}")
    print("Expected locations:")
    print(f"  - {credentials_path}")
    print(f"  - {os.path.join(os.path.dirname(__file__), '..', 'silent-polygon-465403-h9-3a57d36afc97.json')}")

def test_multi_expert_ai_pipeline():
    """Test the complete multi-expert AI pipeline."""
    
    print("=== Testing Multi-Expert AI Pipeline ===")
    
    # Test image path
    test_image_path = os.path.join(os.path.dirname(__file__), 'example.JPG')
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found at {test_image_path}")
        return False
    
    # Test the API endpoint
    api_url = "https://restyleproject-production.up.railway.app/api/ai-image-search/"
    
    print(f"📸 Using test image: {test_image_path}")
    print(f"🌐 Testing API endpoint: {api_url}")
    
    try:
        # Prepare the request
        with open(test_image_path, 'rb') as image_file:
            files = {'image': image_file}
            
            print("🚀 Sending request to multi-expert AI pipeline...")
            start_time = time.time()
            
            response = requests.post(api_url, files=files, timeout=60)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Multi-expert AI pipeline test successful!")
                
                # Analyze the results
                analysis_results = result.get('analysis_results', {})
                
                # Check identified attributes
                identified_attributes = analysis_results.get('identified_attributes', {})
                print(f"\n🔍 Identified Attributes:")
                print(f"   Product Name: {identified_attributes.get('product_name', 'N/A')}")
                print(f"   Brand: {identified_attributes.get('brand', 'N/A')}")
                print(f"   Category: {identified_attributes.get('category', 'N/A')}")
                print(f"   Confidence Score: {identified_attributes.get('confidence_score', 'N/A')}")
                print(f"   AI Summary: {identified_attributes.get('ai_summary', 'N/A')}")
                
                # Check expert agreement
                expert_agreement = identified_attributes.get('expert_agreement', {})
                if expert_agreement:
                    print(f"\n🤝 Expert Agreement:")
                    print(f"   Google Vision Confidence: {expert_agreement.get('google_vision_confidence', 'N/A')}")
                    print(f"   AWS Rekognition Confidence: {expert_agreement.get('aws_rekognition_confidence', 'N/A')}")
                    print(f"   Overall Agreement: {expert_agreement.get('overall_agreement', 'N/A')}")
                
                # Check market query
                market_query = analysis_results.get('market_query_used', 'N/A')
                print(f"\n🔎 Market Query Used: '{market_query}'")
                
                # Check marketplace results
                ranked_comps = analysis_results.get('visually_ranked_comps', [])
                print(f"\n📊 Marketplace Results:")
                print(f"   Total Comps Found: {len(ranked_comps)}")
                
                if ranked_comps:
                    print(f"   Top 3 Results:")
                    for i, comp in enumerate(ranked_comps[:3]):
                        title = comp.get('title', 'N/A')[:50] + '...' if len(comp.get('title', '')) > 50 else comp.get('title', 'N/A')
                        price = comp.get('price', {}).get('value', 'N/A') if isinstance(comp.get('price'), dict) else comp.get('price', 'N/A')
                        visual_score = comp.get('visual_similarity_score', 'N/A')
                        print(f"     {i+1}. {title}")
                        print(f"        Price: {price}")
                        print(f"        Visual Score: {visual_score}")
                
                # Check price analysis
                price_analysis = analysis_results.get('price_analysis', {})
                if price_analysis:
                    print(f"\n💰 Price Analysis:")
                    print(f"   Analysis: {price_analysis.get('price_analysis', 'N/A')}")
                    price_range = price_analysis.get('price_range', {})
                    if price_range:
                        print(f"   Price Range: ${price_range.get('min', 'N/A')} - ${price_range.get('max', 'N/A')}")
                        print(f"   Suggested Price: ${price_analysis.get('suggested_price', 'N/A')}")
                        print(f"   Confidence: {price_analysis.get('confidence', 'N/A')}")
                
                # Check system info
                system_info = result.get('system_info', {})
                if system_info:
                    print(f"\n💻 System Info:")
                    print(f"   Memory Usage: {system_info.get('memory_usage_mb', 'N/A')} MB")
                    print(f"   Peak Memory: {system_info.get('total_memory_peak_mb', 'N/A')} MB")
                
                return True
                
            else:
                print(f"❌ API request failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Django server is running on Railway")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout: The AI pipeline took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_individual_services():
    """Test individual services to isolate any issues."""
    
    print("\n=== Testing Individual Services ===")
    
    try:
        # Test AggregatorService
        print("🔧 Testing AggregatorService...")
        from core.aggregator_service import get_aggregator_service
        
        aggregator = get_aggregator_service()
        print("✅ AggregatorService initialized successfully")
        
        # Test MarketAnalysisService
        print("🔧 Testing MarketAnalysisService...")
        from core.market_analysis_service import get_market_analysis_service
        
        market_analyzer = get_market_analysis_service()
        print("✅ MarketAnalysisService initialized successfully")
        
        # Test encoder service (optional - for visual similarity)
        print("🔧 Testing EncoderService...")
        try:
            from core.encoder_service import get_encoder_service
            encoder = get_encoder_service()
            print("✅ EncoderService initialized successfully")
        except ImportError:
            print("⚠️  EncoderService not available (visual similarity ranking will be disabled)")
        except Exception as e:
            print(f"⚠️  EncoderService error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False

def main():
    """Main test function."""
    
    print("🧪 Multi-Expert AI System Test Suite")
    print("=" * 50)
    
    # Test 1: Individual services
    services_ok = test_individual_services()
    
    if not services_ok:
        print("\n❌ Service tests failed. Check your environment configuration.")
        return False
    
    # Test 2: Complete pipeline
    pipeline_ok = test_multi_expert_ai_pipeline()
    
    if pipeline_ok:
        print("\n🎉 All tests passed! Multi-expert AI system is working correctly.")
        return True
    else:
        print("\n❌ Pipeline test failed. Check the logs for more details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 