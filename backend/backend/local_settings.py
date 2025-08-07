"""
Local settings for development - contains sensitive credentials
"""
import os

try:
    from .local_settings_secrets import *
except ImportError:
    pass

# Google Cloud API key (replacing service account credentials)
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')
GOOGLE_CLOUD_LOCATION = os.environ.get('GOOGLE_CLOUD_LOCATION')

# AWS Rekognition Credentials
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME', 'us-east-1')

# Set environment variables for AWS
if AWS_ACCESS_KEY_ID:
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
if AWS_SECRET_ACCESS_KEY:
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
if AWS_REGION_NAME:
    os.environ['AWS_REGION_NAME'] = AWS_REGION_NAME

# Set environment variable for Google Cloud API key
if GOOGLE_API_KEY:
    os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
if GOOGLE_CLOUD_PROJECT:
    os.environ['GOOGLE_CLOUD_PROJECT'] = GOOGLE_CLOUD_PROJECT
if GOOGLE_CLOUD_LOCATION:
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