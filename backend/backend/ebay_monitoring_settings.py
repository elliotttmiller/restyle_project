"""
eBay Token Monitoring Configuration
Settings for monitoring, alerting, and health checks
"""

# Monitoring Settings
EBAY_MONITORING_ENABLED = True
EBAY_HEALTH_CHECK_INTERVAL = 1800  # 30 minutes in seconds
EBAY_MONITORING_DASHBOARD_ENABLED = True

# Alert Settings
EBAY_ALERT_EMAIL = None  # Set to email address for alerts
EBAY_ALERT_WEBHOOK_URL = None  # Set to webhook URL for alerts
EBAY_ALERT_SLACK_WEBHOOK = None  # Set to Slack webhook URL

# Health Thresholds
EBAY_TOKEN_EXPIRY_WARNING_HOURS = 24  # Warn 24 hours before expiry
EBAY_TOKEN_REFRESH_FAILURE_THRESHOLD = 3  # Alert after 3 consecutive failures
EBAY_TOKEN_VALIDATION_FAILURE_THRESHOLD = 2  # Alert after 2 consecutive failures

# Cache Settings
EBAY_METRICS_CACHE_TIMEOUT = 86400  # 24 hours
EBAY_ALERTS_CACHE_TIMEOUT = 86400  # 24 hours
EBAY_HEALTH_CACHE_TIMEOUT = 3600  # 1 hour

# Task Settings
EBAY_TASK_TIMEOUT = 300  # 5 minutes
EBAY_TASK_RETRY_DELAY = 60  # 1 minute
EBAY_TASK_MAX_RETRIES = 3

# Dashboard Settings
EBAY_DASHBOARD_HISTORY_DAYS = 7  # Keep 7 days of history
EBAY_DASHBOARD_MAX_ALERTS = 50  # Keep last 50 alerts
EBAY_DASHBOARD_REFRESH_INTERVAL = 30  # 30 seconds

# Logging Settings
EBAY_MONITORING_LOG_LEVEL = 'INFO'
EBAY_ALERT_LOG_LEVEL = 'WARNING'
EBAY_HEALTH_LOG_LEVEL = 'INFO'

# Performance Settings
EBAY_METRICS_SAMPLE_RATE = 1.0  # 100% of requests
EBAY_CACHE_ENABLED = True
EBAY_RATE_LIMITING_ENABLED = True

# Integration Settings
EBAY_SLACK_INTEGRATION_ENABLED = False
EBAY_EMAIL_INTEGRATION_ENABLED = False
EBAY_WEBHOOK_INTEGRATION_ENABLED = False

# Development Settings
EBAY_MOCK_MODE = False  # Set to True for testing without real API calls
EBAY_DEBUG_MODE = False  # Set to True for detailed logging 