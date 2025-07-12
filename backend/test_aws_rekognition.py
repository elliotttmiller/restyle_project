#!/usr/bin/env python3
"""
Test script for AWS Rekognition credentials.
This script will test the AWS Rekognition API connection.
"""

import os
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_rekognition():
    """Test AWS Rekognition credentials and API access."""
    print("Testing AWS Rekognition credentials...")
    print("=" * 50)
    
    # Get credentials from environment or use defaults
    access_key = os.environ.get('AWS_ACCESS_KEY_ID', '***REMOVED***')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY', '3LAsYxgRHS0msvNQLdAf7Nnab89j//0oFp2JfEja')
    region = os.environ.get('AWS_REGION_NAME', 'us-east-1')
    
    print(f"Access Key ID: {access_key[:10]}...")
    print(f"Secret Access Key: {secret_key[:10]}...")
    print(f"Region: {region}")
    print()
    
    try:
        # Create Rekognition client
        rekognition = boto3.client(
            'rekognition',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        print("✅ Successfully created Rekognition client")
        
        # Test with a simple API call
        print("Testing API connection...")
        response = rekognition.list_collections(MaxResults=1)
        
        print("✅ AWS Rekognition connection successful!")
        print(f"Response: {response}")
        
        # Test label detection with a sample image if available
        test_image_path = r'C:\Users\AMD\restyle_project\test_files\example2.JPG'
        if os.path.exists(test_image_path):
            print(f"\nTesting label detection with {test_image_path}...")
            
            with open(test_image_path, 'rb') as image:
                image_bytes = image.read()
                
            label_response = rekognition.detect_labels(
                Image={'Bytes': image_bytes},
                MaxLabels=10
            )
            
            print("✅ Label detection successful!")
            print("Detected labels:")
            for label in label_response['Labels']:
                print(f"  - {label['Name']} (Confidence: {label['Confidence']:.1f}%)")
        else:
            print(f"\nNote: Test image {test_image_path} not found. Label detection test skipped.")
        
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
    print("AWS Rekognition Credentials Test")
    print("=" * 40)
    print()
    
    # Test environment setup
    if test_environment_setup():
        print()
        # Test AWS Rekognition
        success = test_aws_rekognition()
        
        if success:
            print("\n🎉 All tests passed! AWS Rekognition is ready to use.")
            print("You can now use the multi-expert AI system with Amazon Rekognition.")
        else:
            print("\n❌ Tests failed. Please check the error messages above.")
            sys.exit(1)
    else:
        print("\n❌ Environment setup failed. Please check the error messages above.")
        sys.exit(1) 