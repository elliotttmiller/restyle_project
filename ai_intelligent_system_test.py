import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

"""
AI-Driven Comprehensive System Test with Intelligent Debugging (Optimized Version)
This script tests the full multi-modal recognition and pricing pipeline using a local image file.
It provides detailed, context-aware debugging output for every stage.
"""
import os
import json
import traceback

# --- CRITICAL: Load environment variables at the very top ---
try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        print(f"INFO: Loading environment variables from {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path, override=True)
    else:
        print("WARNING: .env file not found in project root. Relying on system environment variables.")
except ImportError:
    print("WARNING: python-dotenv not installed. Cannot load .env file.")

# --- Setup Django Environment ---
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.backend.settings')
try:
    django.setup()
except Exception as e:
    print(f"CRITICAL: Failed to setup Django. Ensure script is run from project root. Error: {e}")
    exit(1)

# --- Import your application's services AFTER setup ---
from backend.core.aggregator_service import get_aggregator_service
from backend.core.encoder_service import get_encoder_service

TEST_IMAGE_PATH = "backend/example2.jpeg"

def print_stage(stage_name):
    print(f"\n{'='*20} {stage_name} {'='*20}")

def main():
    print("\n🧪 AI-Driven System Test with Intelligent Debugging\n" + "="*60)
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ CRITICAL FAILURE: Test image not found at: {TEST_IMAGE_PATH}")
        return

    success = True
    try:
        print_stage("1. Encoder: CLIP Embedding & Description")
        encoder = get_encoder_service()
        with open(TEST_IMAGE_PATH, "rb") as f:
            image_bytes = f.read()
        from PIL import Image
        from io import BytesIO
        pil_image = Image.open(BytesIO(image_bytes))
        # Try both new and legacy method names for compatibility
        if hasattr(encoder, 'encode_image') and hasattr(encoder, 'describe_image'):
            embedding = encoder.encode_image(pil_image)
            description = encoder.describe_image(pil_image)
        else:
            embedding = encoder.encode(image_bytes)
            description = encoder.describe(image_bytes)
        if embedding is not None and description is not None:
            print(f"✅ Embedding shape: {getattr(embedding, 'shape', len(embedding) if hasattr(embedding, '__len__') else 'unknown')}")
            print(f"✅ Description: {description}")
        else:
            raise RuntimeError("Encoder service failed to produce both embedding and description.")
    except Exception as e:
        print(f"❌ Encoder failed: {e}\n{traceback.format_exc()}")
        success = False

    if success:
        try:
            print_stage("2. Aggregator: Multi-Expert AI & Gemini Synthesis")
            aggregator = get_aggregator_service()
            import asyncio
            gemini_output = asyncio.run(aggregator.run_full_analysis(image_bytes))
            if "error" in gemini_output:
                raise RuntimeError(f"Aggregator service returned an error: {gemini_output['error']}")
            print("✅ Gemini Output (Structured Dossier):")
            print(json.dumps(gemini_output, indent=2))
            if gemini_output.get('ebay_search_query'):
                print(f"\n🔎 eBay Search Query: {gemini_output['ebay_search_query']}")
            elif gemini_output.get('identified_attributes', {}).get('ebay_search_query'):
                print(f"\n🔎 eBay Search Query: {gemini_output['identified_attributes']['ebay_search_query']}")
            else:
                print("⚠️  No eBay search query found in Gemini output.")
        except Exception as e:
            print(f"❌ Aggregator/Gemini pipeline failed: {e}\n{traceback.format_exc()}")
            success = False

    print("\n" + "="*60)
    if success:
        print("🎉 ✅ SYSTEM TEST PASSED: All core AI pipeline stages completed successfully!")
    else:
        print("🔥 ❌ SYSTEM TEST FAILED: One or more stages failed. See logs above for details.")
    print("="*60)

if __name__ == "__main__":
    main()
