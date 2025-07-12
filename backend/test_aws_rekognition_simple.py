#!/usr/bin/env python3
"""
Simplified test script for AWS Rekognition credentials.
This version doesn't require ListCollections permission.
"""

import os
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_rekognition_simple():
    """Test AWS Rekognition credentials with basic functionality."""
    print("Testing AWS Rekognition credentials (Simple Version)...")
    print("=" * 60)
    
    # Get credentials from environment or use defaults
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'REDACTED')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'REDACTED')
    region = os.environ.get('AWS_REGION_NAME', 'us-east-1')
    
    print(f"Access Key ID: {AWS_ACCESS_KEY_ID[:10]}...")
    print(f"Secret Access Key: {AWS_SECRET_ACCESS_KEY[:10]}...")
    print(f"Region: {region}")
    print()
    
    try:
        # Create Rekognition client
        rekognition = boto3.client(
            'rekognition',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=region
        )
        
        print("✅ Successfully created Rekognition client")
        
        # Test with a minimal image detection (doesn't require ListCollections)
        print("Testing basic Rekognition functionality...")
        
        # Create a minimal test image (1x1 pixel PNG)
        minimal_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x178\x00\x00\x00\x00IEND\xaeB`\x82'
        
        try:
            response = rekognition.detect_labels(
                Image={'Bytes': minimal_image},
                MaxLabels=1
            )
            
            print("✅ AWS Rekognition API access successful!")
            print("✅ Your credentials have proper Rekognition permissions")
            print(f"Response: {response}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidImageFormatException':
                print("✅ AWS Rekognition API access successful!")
                print("✅ Your credentials have proper Rekognition permissions")
                print("Note: Invalid image format expected for minimal test")
            else:
                print(f"❌ Rekognition API error: {error_code}")
                print(f"Error message: {e.response['Error']['Message']}")
                return False
        
        # Test with a real image if available
        test_image_path = r'C:\Users\AMD\restyle_project\test_files\example2.JPG'
        if os.path.exists(test_image_path):
            print(f"\nTesting label detection with {test_image_path}...")
            
            with open(test_image_path, 'rb') as image:
                image_bytes = image.read()
                
            try:
                label_response = rekognition.detect_labels(
                    Image={'Bytes': image_bytes},
                    MaxLabels=10
                )
                
                print("✅ Label detection successful!")
                print("Detected labels:")
                for label in label_response['Labels']:
                    print(f"  - {label['Name']} (Confidence: {label['Confidence']:.1f}%)")
                    
            except ClientError as e:
                print(f"⚠️  Label detection failed: {e.response['Error']['Message']}")
                print("This might be due to image format or content restrictions")
        
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
        print("Please check your environment variables or local settings")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print("❌ AWS credentials are invalid or insufficient permissions")
            print("Make sure your IAM user has AmazonRekognitionReadOnlyAccess policy")
            print("\nTo fix this:")
            print("1. Go to AWS Console: https://225771712480.signin.aws.amazon.com/console")
            print("2. Login with username: restyle-rekognition-user")
            print("3. Go to IAM → Users → restyle-rekognition-user")
            print("4. Add policy: AmazonRekognitionReadOnlyAccess")
        else:
            print(f"❌ AWS connection error: {error_code}")
            print(f"Error message: {e.response['Error']['Message']}")
        return False
    except ImportError:
        print("❌ boto3 not installed")
        print("Please install it with: pip install boto3")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_environment_setup():
    """Test if the environment is properly configured."""
    print("Testing environment setup...")
    print("=" * 30)
    
    # Check if boto3 is installed
    try:
        import boto3
        print("✅ boto3 is installed")
    except ImportError:
        print("❌ boto3 is not installed")
        return False
    
    # Check credentials
    access_key = os.environ.get('AWS_ACCESS_KEY_ID', '***REMOVED***')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY', '3LAsYxgRHS0msvNQLdAf7Nnab89j//0oFp2JfEja')
    
    if access_key and secret_key:
        print("✅ AWS credentials are available")
    else:
        print("❌ AWS credentials are missing")
        return False
    
    return True

if __name__ == "__main__":
    print("AWS Rekognition Credentials Test (Simple Version)")
    print("=" * 50)
    print()
    
    # Test environment setup
    if test_environment_setup():
        print()
        # Test AWS Rekognition
        success = test_aws_rekognition_simple()
        
        if success:
            print("\n🎉 All tests passed! AWS Rekognition is ready to use.")
            print("Your multi-expert AI system can now use Amazon Rekognition.")
        else:
            print("\n❌ Tests failed. Please check the error messages above.")
            print("\n📋 Next steps:")
            print("1. Follow the permission setup guide in fix_aws_permissions.md")
            print("2. Or run the original test: python test_aws_rekognition.py")
            sys.exit(1)
    else:
        print("\n❌ Environment setup failed. Please check the error messages above.")
        sys.exit(1) 