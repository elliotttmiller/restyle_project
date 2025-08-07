# Local secrets for development (DO NOT COMMIT)
# This file is gitignored. Do not share or commit.

import os

# For local development, set these environment variables in your shell or .env file:
#   set GOOGLE_API_KEY=your_google_***REMOVED***_here
#   set AWS_ACCESS_KEY_FILE=D:\AMD\secrets\***REMOVED***

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME', 'us-east-1')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
AWS_ACCESS_KEY_FILE = os.environ.get('AWS_ACCESS_KEY_FILE')
GOOGLE_CLOUD_PROJECT = 'silent-polygon-465403'
GOOGLE_CLOUD_LOCATION = 'us-central1'
# Add any other secrets as needed, e.g. eBay credentials, etc. 