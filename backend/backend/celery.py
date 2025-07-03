# backend/backend/celery.py

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Change this line!
app = Celery('backend') 

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure periodic tasks for eBay token management
app.conf.beat_schedule = {
    # Refresh eBay token every hour
    'refresh-ebay-token-hourly': {
        'task': 'core.tasks.refresh_ebay_token_task',
        'schedule': crontab(minute=0, hour='*/1'),  # Every hour at minute 0
    },
    # Validate eBay token every 30 minutes
    'validate-ebay-token-30min': {
        'task': 'core.tasks.validate_ebay_token_task',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    # Monitor token health daily at 9 AM
    'monitor-ebay-token-daily': {
        'task': 'core.tasks.monitor_ebay_token_health_task',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    # Clean up old token logs weekly
    'cleanup-token-logs-weekly': {
        'task': 'core.tasks.cleanup_token_logs_task',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sunday at 2 AM
    },
}

# Task routing for eBay token management
app.conf.task_routes = {
    'core.tasks.refresh_ebay_token_task': {'queue': 'ebay_tokens'},
    'core.tasks.validate_ebay_token_task': {'queue': 'ebay_tokens'},
    'core.tasks.monitor_ebay_token_health_task': {'queue': 'ebay_tokens'},
    'core.tasks.cleanup_token_logs_task': {'queue': 'ebay_tokens'},
}

# Task settings for eBay token management
app.conf.task_annotations = {
    'core.tasks.refresh_ebay_token_task': {
        'rate_limit': '1/m',  # Max 1 refresh per minute
        'time_limit': 300,    # 5 minute timeout
        'soft_time_limit': 240,  # 4 minute soft timeout
    },
    'core.tasks.validate_ebay_token_task': {
        'rate_limit': '2/m',  # Max 2 validations per minute
        'time_limit': 60,     # 1 minute timeout
    },
    'core.tasks.monitor_ebay_token_health_task': {
        'rate_limit': '1/h',  # Max 1 monitoring per hour
        'time_limit': 120,    # 2 minute timeout
    },
}