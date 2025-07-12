"""
Local settings for environment-specific configuration.
This file should be imported at the bottom of settings.py.
"""
import os

# Google Cloud credentials path
GOOGLE_APPLICATION_CREDENTIALS = r'C:\Users\AMD\restyle_project\backend\silent-polygon-465403-h9-81cb035ed6d4.json'

# The same service account will be used for Vision API, Vertex AI, and Gemini API

# AWS Rekognition Credentials
AWS_CREDENTIALS_PATH = r'C:\Users\AMD\restyle_project\backend\restyle-rekognition-user_accessKeys.csv'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '***REMOVED***')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '3LAsYxgRHS0msvNQLdAf7Nnab89j//0oFp2JfEja')
AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME', 'us-east-1')

# eBay OAuth Credentials
EBAY_PRODUCTION_APP_ID = os.environ.get('EBAY_PRODUCTION_APP_ID', 'ElliottM-Restyle-PRD-f9e7df762-2e54c04b')
EBAY_PRODUCTION_CERT_ID = os.environ.get('EBAY_PRODUCTION_CERT_ID', 'PRD-8e894d8b6739-8cae-4fb6-b103-52ca')
EBAY_PRODUCTION_CLIENT_SECRET = os.environ.get('EBAY_PRODUCTION_CLIENT_SECRET', 'PRD-8e894d8b6739-8cae-4fb6-b103-52ca')
EBAY_PRODUCTION_REFRESH_TOKEN = os.environ.get('EBAY_PRODUCTION_REFRESH_TOKEN', 'v^1.1#i^1#f^0#p^3#I^3#r^1#t^Ul4xMF83OjY2Qzg4N0NDQTg1MUYxQjNDNUVENTBCN0M5QjVBRTI0XzFfMSNFXjI2MA==')
EBAY_PRODUCTION_USER_TOKEN = os.environ.get('EBAY_PRODUCTION_USER_TOKEN', 'v^1.1#i^1#f^0#p^3#I^3#r^0#t^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')  # Fallback token if needed

# Log configuration for new services
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