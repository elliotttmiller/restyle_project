#!/usr/bin/env python3
"""
Test Vertex AI service initialization
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_vertex_ai_service():
    """Test Vertex AI service initialization"""
    print("🔍 TESTING VERTEX AI SERVICE INITIALIZATION")
    print("=" * 50)
    
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        
        import django
        django.setup()
        
        from core.vertex_ai_service import VertexAIService
        
        print("📋 CREATING VERTEX AI SERVICE INSTANCE:")
        
        # Create the service instance
        service = VertexAIService()
        
        print(f"   Vertex AI available: {service.vertex_ai_available}")
        print(f"   Gemini available: {service.gemini_available}")
        
        # Get service status
        status = service.get_service_status()
        print(f"\n📊 SERVICE STATUS:")
        print(f"   Vertex AI: {status.get('vertex_ai_available', False)}")
        print(f"   Gemini: {status.get('gemini_available', False)}")
        print(f"   Recommended service: {status.get('recommended_service', 'unknown')}")
        
        # Test synthesis if available
        if service.gemini_available:
            print("\n🧠 TESTING GEMINI SYNTHESIS:")
            test_data = {
                'google_vision': {
                    'web_entities': [{'description': 'Nike Air Jordan'}],
                    'labels': [{'description': 'Shoe'}],
                    'text': 'Nike Air Jordan 1 Retro'
                },
                'aws_rekognition': {
                    'labels': [{'Name': 'Shoe', 'Confidence': 95.0}],
                    'text': 'Nike Air Jordan'
                }
            }
            
            try:
                result = service.synthesize_expert_opinions(test_data)
                print(f"   ✅ Synthesis successful: {result}")
            except Exception as e:
                print(f"   ❌ Synthesis failed: {e}")
        else:
            print("\n❌ GEMINI NOT AVAILABLE")
            print("   This explains why it shows as 'Inactive' in your status grid")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Vertex AI service: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_vertex_ai_service() 