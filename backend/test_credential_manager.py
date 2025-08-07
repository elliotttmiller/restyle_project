#!/usr/bin/env python3
"""
Test script to verify credential manager functionality
"""
import os
import sys
import django

# Setup Django (should auto-load .env now)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.credential_manager import credential_manager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_credential_manager():
    """Test all credential manager functionality"""
    print("🧪 Testing Credential Manager")
    print("=" * 50)
    
    # Test service status
    print("\n📊 Service Status:")
    status = credential_manager.get_service_status()
    for service, service_status in status.items():
        enabled = service_status.get('enabled', False)
        available = service_status.get('available', False)
        credentials = service_status.get('credentials_valid', False)
        
        status_icon = "✅" if enabled and available and credentials else "❌"
        print(f"  {status_icon} {service}: enabled={enabled}, available={available}, credentials={credentials}")
    
    # Test individual service checks
    print("\n🔍 Individual Service Checks:")
    services = ['google_vision', 'aws_rekognition', 'ebay']
    for service in services:
        enabled = credential_manager.is_service_enabled(service)
        print(f"  {service}: {'✅ Enabled' if enabled else '❌ Disabled'}")
    
    # Test credential retrieval
    print("\n🔑 Credential Retrieval:")
    
    # Google credentials
    google_creds = credential_manager.get_google_credentials()
    print(f"  Google Credentials: {'✅ Available' if google_creds else '❌ Missing'}")
    
    # AWS credentials
    aws_creds = credential_manager.get_aws_credentials()
    has_aws = aws_creds.get('aws_***REMOVED***') and aws_creds.get('aws_***REMOVED***')
    print(f"  AWS Credentials: {'✅ Available' if has_aws else '❌ Missing'}")
    if has_aws:
        print(f"    Region: {aws_creds.get('aws_region', 'Not specified')}")
    
    # eBay credentials
    ebay_creds = credential_manager.get_ebay_credentials()
    has_ebay = ebay_creds.get('app_id') and ebay_creds.get('***REMOVED***')
    print(f"  eBay Credentials: {'✅ Available' if has_ebay else '❌ Missing'}")
    
    # Test validation
    print("\n🔍 Credential Validation:")
    validation = credential_manager.validate_credentials()
    for service, is_valid in validation.items():
        print(f"  {service}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Print summary report
    print("\n📋 Summary Report:")
    summary = credential_manager.get_summary_report()
    print(f"  Loaded Credentials: {summary['loaded_credentials']}")
    print(f"  Enabled Services: {summary['enabled_services']}")
    print(f"  Validated Services: {summary['validated_services']}")
    print(f"  Available Services: {summary['available_services']}")
    
    print("\n✅ Credential Manager Test Complete!")

if __name__ == "__main__":
    test_credential_manager()
