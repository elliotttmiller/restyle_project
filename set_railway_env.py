#!/usr/bin/env python3
"""
Railway Environment Variable Setup Script
Run this script to set all required environment variables in Railway
"""

import os
from dotenv import load_dotenv

# Load local .env file
load_dotenv()

# Environment variables to set in Railway
env_vars = {
    # AWS Credentials
    'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
    'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'AWS_REGION': os.getenv('AWS_REGION'),
    'AWS_DEFAULT_REGION': os.getenv('AWS_DEFAULT_REGION'),
    
    # Google Cloud
    'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
    
    # eBay Integration
    'EBAY_PRODUCTION_APP_ID': os.getenv('EBAY_PRODUCTION_APP_ID'),
    'EBAY_PRODUCTION_CERT_ID': os.getenv('EBAY_PRODUCTION_CERT_ID'),
    'EBAY_PRODUCTION_CLIENT_SECRET': os.getenv('EBAY_PRODUCTION_CLIENT_SECRET'),
    'EBAY_PRODUCTION_REFRESH_TOKEN': os.getenv('EBAY_PRODUCTION_REFRESH_TOKEN'),
    'EBAY_SANDBOX': os.getenv('EBAY_SANDBOX', 'False'),
    
    # Database (Railway provides this automatically)
    # 'DATABASE_URL': os.getenv('DATABASE_URL'),
    
    # Other services
    'PINECONE_API_KEY': os.getenv('PINECONE_API_KEY'),
    'PINECONE_ENVIRONMENT': os.getenv('PINECONE_ENVIRONMENT'),
    'PINECONE_INDEX_NAME': os.getenv('PINECONE_INDEX_NAME'),
}

print("Railway Environment Variables to Set:")
print("=" * 50)

railway_commands = []
for key, value in env_vars.items():
    if value:
        print(f"{key}={value}")
        railway_commands.append(f'railway variables set {key}="{value}"')
    else:
        print(f"{key}=NOT_SET")

print("\n" + "=" * 50)
print("Railway CLI Commands:")
print("=" * 50)

for cmd in railway_commands:
    print(cmd)

print("\n" + "=" * 50)
print("Manual Setup Instructions:")
print("=" * 50)
print("1. Go to your Railway project dashboard")
print("2. Click on 'Variables' tab")
print("3. Add each environment variable listed above")
print("4. Redeploy your application")