"""
eBay Token Refresh Configuration
Settings for automatic token management
"""

# Token refresh settings
EBAY_TOKEN_REFRESH_ENABLED = True
EBAY_TOKEN_REFRESH_BUFFER_HOURS = 1  # Refresh 1 hour before expiry
EBAY_TOKEN_CACHE_TIMEOUT = 7200  # 2 hours in seconds

# Celery task scheduling (in seconds)
EBAY_TOKEN_REFRESH_INTERVAL = 3600  # 1 hour
EBAY_TOKEN_VALIDATION_INTERVAL = 1800  # 30 minutes

# Retry settings
EBAY_TOKEN_REFRESH_MAX_RETRIES = 3
EBAY_TOKEN_REFRESH_RETRY_DELAY = 300  # 5 minutes

# Monitoring settings
EBAY_TOKEN_MONITORING_ENABLED = True
EBAY_TOKEN_EXPIRY_ALERT_HOURS = 24  # Alert 24 hours before expiry

# Fallback settings
EBAY_TOKEN_FALLBACK_ENABLED = True
EBAY_TOKEN_FALLBACK_TO_SETTINGS = True

# Logging settings
EBAY_TOKEN_LOGGING_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR 