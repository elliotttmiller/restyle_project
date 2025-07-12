# Fix AWS Rekognition Permissions

## Issue
Your AWS user `restyle-rekognition-user` doesn't have the proper permissions to use Rekognition API.

## Solution

### 1. Log into AWS Console
Go to: https://225771712480.signin.aws.amazon.com/console
- Username: `restyle-rekognition-user`
- Password: `E$$io$$2`

### 2. Navigate to IAM
1. Click on your username in the top right
2. Click "Security credentials"
3. Or go directly to IAM: https://console.aws.amazon.com/iam/

### 3. Add Rekognition Permissions

#### Option A: Attach Existing Policy (Recommended)
1. Go to IAM → Users → `restyle-rekognition-user`
2. Click "Add permissions"
3. Choose "Attach policies directly"
4. Search for and select: `AmazonRekognitionReadOnlyAccess`
5. Click "Next" and "Add permissions"

#### Option B: Create Custom Policy
If the above policy doesn't exist, create a custom policy:

1. Go to IAM → Policies → Create policy
2. Use JSON editor and paste this:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rekognition:DetectLabels",
                "rekognition:DetectText",
                "rekognition:DetectFaces",
                "rekognition:DetectModerationLabels",
                "rekognition:ListCollections",
                "rekognition:DescribeCollections"
            ],
            "Resource": "*"
        }
    ]
}
```
3. Name it: `RekognitionAccessPolicy`
4. Attach it to your user

### 4. Test Again
After adding permissions, run the test again:
```bash
cd backend
python test_aws_rekognition.py
```

## Alternative: Use Different Test
If you want to test without `ListCollections`, we can modify the test to use `DetectLabels` directly:

```python
# Test with a simple image detection instead
response = rekognition.detect_labels(
    Image={'Bytes': b'test'},  # Minimal test
    MaxLabels=1
)
```

## Quick Fix Script
I can create a modified test script that doesn't require `ListCollections` permission if you prefer to test the core functionality first. 