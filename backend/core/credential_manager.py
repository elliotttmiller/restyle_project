"""
Secure Credential Manager
Handles loading credentials from environment variables and files safely.
"""

import os
import json
import csv
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CredentialManager:
    """Manages credentials securely"""
    
    def __init__(self):
        self.credentials = {}
        self.load_credentials()
    
    def load_credentials(self):
        """Load all credentials from environment and files"""
        try:
            # Load from environment variables
            self._load_from_env()
            
            # Load from credential files
            self._load_google_credentials()
            self._load_aws_credentials()
            
            logger.info("✅ Credentials loaded successfully")
        except Exception as e:
            logger.error(f"❌ Error loading credentials: {e}")
    
    def _load_from_env(self):
        """Load credentials from environment variables"""
        env_credentials = {
            'aws_***REMOVED***': os.environ.get('AWS_ACCESS_KEY_ID'),
            'aws_***REMOVED***': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'aws_region': os.environ.get('AWS_REGION') or os.environ.get('AWS_REGION_NAME') or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'),
            'ebay_app_id': os.environ.get('EBAY_PRODUCTION_APP_ID') or os.environ.get('EBAY_CLIENT_ID'),
            'ebay_cert_id': os.environ.get('EBAY_PRODUCTION_CERT_ID') or os.environ.get('EBAY_CERT_ID'),
            'ebay_***REMOVED***': os.environ.get('EBAY_PRODUCTION_CLIENT_SECRET') or os.environ.get('EBAY_CLIENT_SECRET'),
            'ebay_refresh_token': os.environ.get('EBAY_PRODUCTION_REFRESH_TOKEN') or os.environ.get('EBAY_REFRESH_TOKEN'),
            'ebay_user_token': os.environ.get('EBAY_PRODUCTION_USER_TOKEN'),
            'google_project': os.environ.get('GOOGLE_CLOUD_PROJECT'),
            'google_location': os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1'),
            # Service enable/disable flags
            'enable_ebay_service': os.environ.get('ENABLE_EBAY_SERVICE', 'True').lower() == 'true',
            'enable_google_vision': os.environ.get('ENABLE_GOOGLE_VISION', 'True').lower() == 'true',
            'enable_aws_rekognition': os.environ.get('ENABLE_AWS_REKOGNITION', 'True').lower() == 'true',
            'enable_ai_services': os.environ.get('ENABLE_AI_SERVICES', 'True').lower() == 'true',
        }
        
        # Filter out None values
        self.credentials.update({k: v for k, v in env_credentials.items() if v})
    
    def _load_google_credentials(self):
        """Load Google Cloud credentials from file"""
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path and Path(creds_path).exists():
            try:
                with open(creds_path, 'r') as f:
                    google_creds = json.load(f)
                self.credentials['google_credentials'] = google_creds
                logger.info("✅ Google Cloud credentials loaded")
            except Exception as e:
                logger.warning(f"⚠️  Could not load Google credentials: {e}")
    
    def _load_aws_credentials(self):
        """Load AWS credentials from file"""
        creds_path = os.environ.get('AWS_CREDENTIALS_PATH')
        if creds_path and Path(creds_path).exists():
            try:
                with open(creds_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'Access key ID' in row and 'Secret access key' in row:
                            self.credentials['aws_***REMOVED***'] = row['Access key ID']
                            self.credentials['aws_***REMOVED***'] = row['Secret access key']
                            break
                logger.info("✅ AWS credentials loaded")
            except Exception as e:
                logger.warning(f"⚠️  Could not load AWS credentials: {e}")
    
    def get_aws_credentials(self) -> Dict[str, str]:
        """Get AWS credentials"""
        return {
            'aws_***REMOVED***': self.credentials.get('aws_***REMOVED***'),
            'aws_***REMOVED***': self.credentials.get('aws_***REMOVED***'),
            'region_name': self.credentials.get('aws_region', 'us-east-1')
        }
    
    def get_ebay_credentials(self) -> Dict[str, str]:
        """Get eBay credentials"""
        return {
            'app_id': self.credentials.get('ebay_app_id'),
            'cert_id': self.credentials.get('ebay_cert_id'),
            '***REMOVED***': self.credentials.get('ebay_***REMOVED***'),
            'refresh_token': self.credentials.get('ebay_refresh_token'),
            'user_token': self.credentials.get('ebay_user_token')
        }
    
    def get_google_credentials(self) -> Optional[Dict[str, Any]]:
        """Get Google Cloud credentials"""
        return self.credentials.get('google_credentials')
    
    def is_service_enabled(self, service_name: str) -> bool:
        """Check if a service is enabled"""
        service_flags = {
            'ebay': self.credentials.get('enable_ebay_service', True),
            'google_vision': self.credentials.get('enable_google_vision', True),
            'aws_rekognition': self.credentials.get('enable_aws_rekognition', True),
            'ai_services': self.credentials.get('enable_ai_services', True),
        }
        return service_flags.get(service_name, True)
    
    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed service status"""
        validation = self.validate_credentials()
        return {
            'aws_rekognition': {
                'enabled': self.is_service_enabled('aws_rekognition'),
                'credentials_valid': validation['aws'],
                'available': self.is_service_enabled('aws_rekognition') and validation['aws']
            },
            'ebay_api': {
                'enabled': self.is_service_enabled('ebay'),
                'credentials_valid': validation['ebay'],
                'available': self.is_service_enabled('ebay') and validation['ebay']
            },
            'google_vision': {
                'enabled': self.is_service_enabled('google_vision'),
                'credentials_valid': validation['google'],
                'available': self.is_service_enabled('google_vision') and validation['google']
            }
        }
    
    def validate_credentials(self) -> Dict[str, bool]:
        """Validate all credentials"""
        validation = {
            'aws': bool(self.credentials.get('aws_***REMOVED***') and self.credentials.get('aws_***REMOVED***')),
            'ebay': bool(self.credentials.get('ebay_app_id') and self.credentials.get('ebay_***REMOVED***') and self.credentials.get('ebay_refresh_token')),
            'google': bool(self.credentials.get('google_credentials'))
        }
        
        logger.info(f"🔍 Credential validation: {validation}")
        return validation
    
    def get_status(self) -> Dict[str, Any]:
        """Get credential status"""
        validation = self.validate_credentials()
        return {
            'credentials_loaded': len(self.credentials) > 0,
            'validation': validation,
            'services_available': {
                'aws_rekognition': validation['aws'],
                'ebay_api': validation['ebay'],
                'google_vision': validation['google'],
                'google_gemini': validation['google'],
                'google_vertex': validation['google']
            }
        }

    def get_summary_report(self) -> Dict[str, Any]:
        """Get a summary report of credential manager status"""
        validation = self.validate_credentials()
        status = self.get_service_status()
        
        return {
            'loaded_credentials': len([k for k, v in self.credentials.items() if v]),
            'enabled_services': len([k for k, v in status.items() if v.get('enabled', False)]),
            'validated_services': len([k for k, v in validation.items() if v]),
            'available_services': len([k for k, v in status.items() if v.get('available', False)])
        }

# Global credential manager instance
credential_manager = CredentialManager() 