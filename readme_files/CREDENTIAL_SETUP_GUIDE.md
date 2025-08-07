# Credential Setup Guide for Multi-Expert AI System

This guide will help you set up all the required credentials for the enhanced multi-expert AI system with Amazon Rekognition, Google Gemini API, and Google Cloud Vertex AI.

## Overview

Your system now uses three AI services:
1. **Google Vision API** (already configured)
2. **Amazon Rekognition** (new)
3. **Google Gemini API** (new)
4. **Google Cloud Vertex AI** (enhanced)

## 1. Google Cloud Setup (Already Configured)

### ✅ Current Status
You already have a Google Cloud service account configured:
- **Project ID**: `silent-polygon-465403-h9`
- **Service Account**: `restyle@silent-polygon-465403-h9.iam.gserviceaccount.com`
- **Credentials File**: `silent-polygon-465403-h9-3a57d36afc97.json`

### 🔧 Enable Additional APIs
You need to enable these APIs in your Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `silent-polygon-465403-h9`
3. Go to "APIs & Services" > "Library"
4. Enable these APIs:
   - ✅ **Cloud Vision API** (already enabled)
   - 🔧 **Vertex AI API** (enable this)
   - 🔧 **Generative AI API** (enable this)

### 📝 Steps to Enable APIs:
```bash
# Option 1: Using gcloud CLI
gcloud auth activate-service-account --key-file=silent-polygon-465403-h9-3a57d36afc97.json
gcloud config set project silent-polygon-465403-h9
gcloud services enable aiplatform.googleapis.com
gcloud services enable generativelanguage.googleapis.com

# Option 2: Using Google Cloud Console
# 1. Go to https://console.cloud.google.com/apis/library
# 2. Search for "Vertex AI API" and enable
# 3. Search for "Generative AI API" and enable
```

## 2. Google Gemini API Setup

### 🔑 Get Gemini API Key

1. **Go to Google AI Studio**:
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account

2. **Create API Key**:
   - Click "Get API key"
   - Select your project: `silent-polygon-465403-h9`
   - Copy the generated API key

3. **Add to Environment**:
   ```bash
   # Add to your .env file or environment variables
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### 🧪 Test Gemini API
```bash
# Test the API key
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_GEMINI_API_KEY" \
     -d '{"contents":[{"parts":[{"text":"Hello, world!"}]}]}' \
     https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent
```

## 3. Amazon AWS Setup

### 🔑 Create AWS Account (if needed)
1. Go to [AWS Console](https://aws.amazon.com/)
2. Sign up for an account if you don't have one
3. Complete the registration process

### 🔧 Create IAM User for Rekognition

1. **Go to IAM Console**:
   - Visit: https://console.aws.amazon.com/iam/
   - Sign in to your AWS account

2. **Create New User**:
   - Click "Users" > "Create user"
   - Enter username: `restyle-rekognition-user`
   - Select "Programmatic access"

3. **Attach Permissions**:
   - Click "Attach policies directly"
   - Search for and select: `AmazonRekognitionReadOnlyAccess`
   - Click "Next" and "Create user"

4. **Save Credentials**:
   - **Access Key ID**: Copy this
   - **Secret Access Key**: Copy this (you won't see it again!)

### 🔧 Set Up AWS Credentials

```bash
# Option 1: Environment Variables
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_REGION_NAME=us-east-1

# Option 2: AWS CLI Configuration
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Enter region: us-east-1
# Enter output format: json
```

### 🧪 Test AWS Rekognition
```bash
# Test with AWS CLI
aws rekognition detect-labels --image-bytes fileb://test_image.jpg

# Or test with Python
python -c "
import boto3
client = boto3.client('rekognition')
response = client.detect_labels(Image={'Bytes': open('test_image.jpg', 'rb').read()})
print(response)
"
```

## 4. Environment Configuration

### 📝 Create Environment File
Create a `.env` file in your project root:

```bash
# Google Cloud (already configured)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/silent-polygon-465403-h9-3a57d36afc97.json

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# AWS Rekognition
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION_NAME=us-east-1
```

### 🔧 Docker Environment
Your `docker-compose.yml` already includes these environment variables:

```yaml
environment:
  - GOOGLE_APPLICATION_CREDENTIALS=/app/silent-polygon-465403-h9-3a57d36afc97.json
  - GEMINI_API_KEY=${GEMINI_API_KEY}
  - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
  - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  - AWS_REGION_NAME=${AWS_REGION_NAME:-us-east-1}
```

## 5. Testing Your Setup

### 🧪 Run the Test Script
```bash
cd test_files
python test_multi_expert_ai.py
```

### 🔍 Check Service Status
```python
# Test individual services
from core.vertex_ai_service import get_vertex_ai_service
vertex_service = get_vertex_ai_service()
status = vertex_service.get_service_status()
print(status)
```

## 6. Troubleshooting

### ❌ Common Issues

#### **Google Cloud Issues**
```bash
# Check if service account has proper permissions
gcloud auth activate-service-account --key-file=silent-polygon-465403-h9-3a57d36afc97.json
gcloud projects get-iam-policy silent-polygon-465403-h9
```

#### **AWS Issues**
```bash
# Test AWS credentials
aws sts get-caller-identity

# Check Rekognition permissions
aws rekognition list-collections
```

#### **Gemini API Issues**
```bash
# Test Gemini API key
curl -H "Authorization: Bearer YOUR_GEMINI_API_KEY" \
     https://generativelanguage.googleapis.com/v1beta/models
```

### 🔧 Debug Mode
Enable detailed logging:
```python
import logging
logging.getLogger('core.aggregator_service').setLevel(logging.DEBUG)
logging.getLogger('core.vertex_ai_service').setLevel(logging.DEBUG)
```

## 7. Cost Optimization

### 💰 Estimated Costs

| Service | Cost per 1000 requests |
|---------|------------------------|
| **Google Vision API** | $1.50 |
| **AWS Rekognition** | $1.00 |
| **Google Gemini API** | $0.50 |
| **Vertex AI** | $2.00+ (varies by model) |

### 🎯 Cost-Saving Tips
1. **Use caching** for repeated analyses
2. **Implement rate limiting** to avoid excessive API calls
3. **Monitor usage** with Google Cloud and AWS billing alerts
4. **Use fallback synthesis** when high-cost services fail

## 8. Security Best Practices

### 🔒 Credential Security
1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Rotate API keys** regularly
4. **Use least-privilege permissions**

### 🛡️ AWS Security
```bash
# Create a more restrictive IAM policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:DetectLabels",
        "rekognition:DetectText"
      ],
      "Resource": "*"
    }
  ]
}
```

## 9. Next Steps

### 🚀 After Setup
1. **Test the complete pipeline** with real images
2. **Monitor performance** and costs
3. **Fine-tune prompts** for better results
4. **Consider custom models** on Vertex AI for specific use cases

### 📈 Advanced Features
- **Custom model training** on Vertex AI
- **Batch processing** for multiple images
- **Real-time learning** from user feedback
- **Multi-marketplace integration** (Poshmark, Grailed, etc.)

## Summary

Your enhanced multi-expert AI system now supports:
- ✅ **Google Vision API** (already working)
- 🔧 **Amazon Rekognition** (new)
- 🔧 **Google Gemini API** (new)
- 🔧 **Google Cloud Vertex AI** (enhanced)

This gives you the most sophisticated AI analysis pipeline available, with multiple expert opinions synthesized by advanced AI reasoning.

**Ready to test your setup?** Run the test script to validate everything is working correctly! 