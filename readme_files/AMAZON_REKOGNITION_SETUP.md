# Amazon Rekognition Setup Guide

Since you already have Google Cloud credentials configured, you only need to set up Amazon Rekognition. Here's the complete setup process:

## **Step 1: Create AWS Account (if needed)**

1. Go to [AWS Console](https://aws.amazon.com/)
2. Click "Create an AWS Account" if you don't have one
3. Complete the registration process
4. Sign in to your AWS account

## **Step 2: Create IAM User for Rekognition**

### **2.1 Go to IAM Console**
- Visit: https://console.aws.amazon.com/iam/
- Sign in to your AWS account

### **2.2 Create New User**
1. Click **"Users"** in the left sidebar
2. Click **"Create user"**
3. Enter username: `restyle-rekognition-user`
4. Select **"Programmatic access"** (for API access)
5. Click **"Next: Permissions"**

### **2.3 Attach Permissions**
1. Click **"Attach policies directly"**
2. Search for: `AmazonRekognitionReadOnlyAccess`
3. Check the box next to it
4. Click **"Next: Tags"** (optional)
5. Click **"Next: Review"**
6. Click **"Create user"**

### **2.4 Save Credentials**
**⚠️ IMPORTANT: Save these credentials immediately - you won't see the secret key again!**

- **Access Key ID**: Copy this (starts with `AKIA...`)
- **Secret Access Key**: Copy this (longer string)

## **Step 3: Configure Environment Variables**

### **Option A: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_***REMOVED***_here
export AWS_SECRET_ACCESS_KEY=your_***REMOVED***_here
export AWS_REGION_NAME=us-east-1
```

### **Option B: AWS CLI Configuration**
```bash
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Enter region: us-east-1
# Enter output format: json
```

### **Option C: Docker Environment**
Your `docker-compose.yml` already includes these variables:
```yaml
environment:
  - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
  - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  - AWS_REGION_NAME=${AWS_REGION_NAME:-us-east-1}
```

## **Step 4: Test Your Setup**

### **4.1 Test with AWS CLI**
```bash
# Test basic connectivity
aws sts get-caller-identity

# Test Rekognition permissions
aws rekognition list-collections
```

### **4.2 Test with Python**
```python
import boto3

# Test Rekognition client
client = boto3.client('rekognition')

# Test with a sample image (optional)
# response = client.detect_labels(
#     Image={'Bytes': open('test_image.jpg', 'rb').read()}
# )
# print(response)
```

### **4.3 Test Complete System**
```bash
cd test_files
python test_multi_expert_ai.py
```

## **Step 5: Enable Required APIs**

### **5.1 Enable Google APIs (if not already done)**
```bash
# Using your existing Google Cloud credentials
gcloud auth activate-service-account --key-file=***REMOVED***
gcloud config set project silent-polygon-465403-h9

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable generativelanguage.googleapis.com
```

## **Step 6: Verify Everything Works**

### **6.1 Check Service Status**
```python
from core.vertex_ai_service import get_vertex_ai_service

vertex_service = get_vertex_ai_service()
status = vertex_service.get_service_status()
print(status)
```

### **6.2 Expected Output**
```json
{
  "vertex_ai_available": true,
  "gemini_available": true,
  "project_id": "silent-polygon-465403-h9",
  "location": "us-central1",
  "recommended_service": "vertex_ai"
}
```

## **Troubleshooting**

### **❌ Common Issues**

#### **AWS Credentials Error**
```bash
# Check if credentials are set
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY

# Test AWS CLI
aws sts get-caller-identity
```

#### **Google Cloud API Issues**
```bash
# Check if APIs are enabled
gcloud services list --enabled | grep -E "(aiplatform|generativelanguage)"

# Enable if needed
gcloud services enable aiplatform.googleapis.com
gcloud services enable generativelanguage.googleapis.com
```

#### **Permission Issues**
```bash
# Test Rekognition permissions
aws rekognition detect-labels --image-bytes fileb://test_image.jpg
```

### **🔧 Debug Mode**
```python
import logging
logging.getLogger('core.aggregator_service').setLevel(logging.DEBUG)
logging.getLogger('core.vertex_ai_service').setLevel(logging.DEBUG)
```

## **Cost Information**

### **💰 AWS Rekognition Pricing**
- **DetectLabels**: $1.00 per 1,000 images
- **DetectText**: $1.50 per 1,000 images
- **Free Tier**: 5,000 images per month for first 12 months

### **💰 Google Services Pricing**
- **Vision API**: $1.50 per 1,000 images
- **Vertex AI**: $2.00+ per 1,000 requests (varies by model)
- **Gemini API**: $0.50 per 1,000 requests

## **Security Best Practices**

### **🔒 AWS Security**
1. **Use least-privilege permissions** (already done with ReadOnlyAccess)
2. **Rotate access keys** regularly
3. **Monitor usage** with AWS CloudTrail
4. **Set up billing alerts** to avoid unexpected charges

### **🛡️ Google Cloud Security**
1. **Your existing service account** already has proper permissions
2. **No additional setup needed** for Google services

## **Summary**

### **✅ What's Already Configured**
- **Google Vision API**: ✅ Working
- **Google Cloud Service Account**: ✅ Configured
- **Docker Environment**: ✅ Updated

### **🔧 What You Need to Set Up**
- **AWS Account**: Create if needed
- **IAM User**: With Rekognition permissions
- **AWS Credentials**: Access Key ID + Secret Access Key
- **Google APIs**: Enable Vertex AI and Generative AI APIs

### **🚀 After Setup**
1. **Test the complete pipeline** with real images
2. **Monitor costs** with AWS and Google Cloud billing
3. **Fine-tune the system** based on performance

## **Quick Start Commands**

```bash
# 1. Set up AWS credentials
export AWS_ACCESS_KEY_ID=your_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_here

# 2. Enable Google APIs
gcloud services enable aiplatform.googleapis.com generativelanguage.googleapis.com

# 3. Test the system
cd test_files
python test_multi_expert_ai.py
```

**That's it!** Your multi-expert AI system will now use:
- **Google Vision API** (existing)
- **Amazon Rekognition** (new)
- **Google Vertex AI** (enhanced)
- **Google Gemini API** (enhanced)

All using your existing Google Cloud credentials for maximum simplicity and security. 