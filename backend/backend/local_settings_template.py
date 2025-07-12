"""
Template for local settings - copy to local_settings.py and add your credentials
"""
import os

# Google Cloud credentials path
GOOGLE_APPLICATION_CREDENTIALS = r'path/to/your/google-credentials.json'

# AWS Rekognition Credentials
AWS_CREDENTIALS_PATH = r'path/to/your/aws-credentials.csv'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'your-aws-access-key')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'your-aws-secret-key')
AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME', 'us-east-1')

# eBay OAuth Credentials
EBAY_PRODUCTION_APP_ID = os.environ.get('EBAY_PRODUCTION_APP_ID', 'your-ebay-app-id')
EBAY_PRODUCTION_CERT_ID = os.environ.get('EBAY_PRODUCTION_CERT_ID', 'your-ebay-cert-id')
EBAY_PRODUCTION_CLIENT_SECRET = os.environ.get('EBAY_PRODUCTION_CLIENT_SECRET', 'your-ebay-client-secret')
EBAY_PRODUCTION_REFRESH_TOKEN = os.environ.get('EBAY_PRODUCTION_REFRESH_TOKEN', 'your-ebay-refresh-token')
EBAY_PRODUCTION_USER_TOKEN = os.environ.get('EBAY_PRODUCTION_USER_TOKEN', 'your-ebay-user-token')

# Log configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'core.aggregator_service': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'core.market_analysis_service': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'core.vertex_ai_service': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
} 