"""
Local settings for development - contains sensitive credentials
"""
import os

# Google Cloud credentials path
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'silent-polygon-465403-h9-3a57d36afc97.json')

# AWS Rekognition Credentials
AWS_ACCESS_KEY_ID = 'AKIATJEIK57QFHCF5KUJ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION_NAME = 'us-east-1'

# Google Cloud Project Configuration
GOOGLE_CLOUD_PROJECT = 'silent-polygon-465403'
GOOGLE_CLOUD_LOCATION = 'us-central1'

# eBay OAuth Credentials (already in main settings, but can override here if needed)
# EBAY_PRODUCTION_APP_ID = os.environ.get('EBAY_PRODUCTION_APP_ID', 'ElliottM-Restyle-PRD-f9e7df762-2e54c04b')
# EBAY_PRODUCTION_CERT_ID = os.environ.get('EBAY_PRODUCTION_CERT_ID', 'PRD-8e894d8b6739-8cae-4fb6-b103-52ca')
# EBAY_PRODUCTION_CLIENT_SECRET = os.environ.get('EBAY_PRODUCTION_CLIENT_SECRET', 'PRD-8e894d8b6739-8cae-4fb6-b103-52ca')
# EBAY_PRODUCTION_REFRESH_TOKEN = os.environ.get('EBAY_PRODUCTION_REFRESH_TOKEN', 'v^1.1#i^1#f^0#p^3#I^3#r^1#t^Ul4xMF83OjY2Qzg4N0NDQTg1MUYxQjNDNUVENTBCN0M5QjVBRTI0XzFfMSNFXjI2MA==')
# EBAY_PRODUCTION_USER_TOKEN = os.environ.get('EBAY_PRODUCTION_USER_TOKEN', 'v^1.1#i^1#f^0#p^3#I^3#r^0#t^H4sIAAAAAAAA/+VZW2wcVxn22k6qtLEbCmlQuZlJWwnM7J6Z2ZnZHdkma3tTb+L12rvr2IkE5szMGfvYc8vMGa+3COE4bYNQqr4A7QNRTB8ARUJUvaQRDyC14hJ6SdUHKFUaEEhtJBBSoE2hoMKZXdvZuG1i7wZ1JfZlNf/8t+8//2XOOWBx67bPPzD0wNsdkZtalxfBYmskwt0Ctm3d0t3Z1nrHlhZQwxBZXrxzsX2pL3zjC97snwunHlqaulj4z76jLZmn3wavn/9ybvmrL+XvvD2N//bp3//k3WxuYP+to9ZrO39+8uj5mx9/5cJvznTs8W7bveP7Z+8RrEs37fleevzZoFsev6tTePfmHzxoPHlfzwWzupb/BVnKsROTHgAA')

# Set environment variables for AWS
os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
os.environ['AWS_REGION_NAME'] = AWS_REGION_NAME

# Set environment variable for Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS
os.environ['GOOGLE_CLOUD_PROJECT'] = GOOGLE_CLOUD_PROJECT
os.environ['GOOGLE_CLOUD_LOCATION'] = GOOGLE_CLOUD_LOCATION

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
        'core.ai_service': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

try:
    from .local_settings_secrets import *
except ImportError:
    pass 