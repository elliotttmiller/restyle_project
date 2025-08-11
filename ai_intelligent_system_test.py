
"""
AI-Driven Comprehensive System Test with Intelligent Debugging
This script tests the full multi-modal recognition and pricing pipeline using a local image file.
It provides detailed, context-aware debugging output for every stage.
"""
import os
import traceback
# Ensure .env variables are loaded for all environments
try:
    from dotenv import load_dotenv
    # Try both project root and backend/.env
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'), override=True)
except ImportError:
    print("[WARNING] python-dotenv not installed. Environment variables may not be loaded from .env.")
from backend.core.encoder_service import AdvancedImageEncoder
# Import other relevant modules as needed (aggregator, market analysis, etc.)

TEST_IMAGE_PATH = "backend/test_example.JPG"

def print_stage(stage):
    print(f"\n{'='*20} {stage} {'='*20}")

def main():
    print("\n🧪 AI-Driven System Test with Intelligent Debugging\n" + "="*60)
    # Debug: Print environment variable status
    print(f"[DEBUG] GEMINI_API_KEY: {os.environ.get('GEMINI_API_KEY')}")
    print(f"[DEBUG] GOOGLE_API_KEY: {os.environ.get('GOOGLE_API_KEY')}")
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
        return
    try:
        print_stage("1. Encoder: CLIP Embedding & Description")
        encoder = AdvancedImageEncoder()
        with open(TEST_IMAGE_PATH, "rb") as f:
            image_bytes = f.read()
        embedding = encoder.encode(image_bytes)
        description = encoder.describe(image_bytes)
        print(f"✅ Embedding shape: {len(embedding)}")
        print(f"✅ Description: {description}")
    except Exception as e:
        print(f"❌ Encoder failed: {e}\n{traceback.format_exc()}")
        return

    try:
        print_stage("2. Aggregator: Multi-Expert AI & Gemini Synthesis")
        from backend.core.aggregator_service import get_aggregator_service
        aggregator = get_aggregator_service()
        gemini_output = aggregator.run_full_analysis(image_bytes)
        print(f"✅ Gemini Output (Structured Dossier):\n{gemini_output}")
        if 'ebay_search_query' in gemini_output:
            print(f"\n🔎 eBay Search Query: {gemini_output['ebay_search_query']}")
        elif 'identified_attributes' in gemini_output and 'ebay_search_query' in gemini_output['identified_attributes']:
            print(f"\n🔎 eBay Search Query: {gemini_output['identified_attributes']['ebay_search_query']}")
        else:
            print("⚠️  No eBay search query found in Gemini output.")
    except Exception as e:
        print(f"❌ Aggregator/Gemini pipeline failed: {e}\n{traceback.format_exc()}")
        return

    print("\n🎉 All core AI pipeline stages passed!\n")

if __name__ == "__main__":
    main()
