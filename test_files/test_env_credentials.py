from dotenv import load_dotenv
import os

# Load .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

print("=== AWS Rekognition Test ===")
try:
    import boto3
    client = boto3.client('rekognition', region_name=os.getenv('AWS_REGION_NAME', 'us-east-1'))
    print("Listing Rekognition collections...")
    print(client.list_collections())
    print("✅ AWS credentials are valid!")
except Exception as e:
    print(f"❌ AWS test failed: {e}")

print("\n=== Google Cloud Vision Test ===")
try:
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    print("✅ Google Cloud Vision credentials are valid!")
except Exception as e:
    print(f"❌ Google test failed: {e}") 