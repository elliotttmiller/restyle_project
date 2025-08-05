"""
Production settings for backend project.
"""

from .base import *
import dj_database_url

# Production must have SECRET_KEY
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production")

# Strict allowed hosts for production
ALLOWED_HOSTS = [
    'restyleproject-production.up.railway.app',
    'restyle-backend.onrender.com',
]

# Add any additional allowed hosts from environment
additional_hosts = os.environ.get('ADDITIONAL_ALLOWED_HOSTS', '')
if additional_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in additional_hosts.split(',')])

# Database - Use DATABASE_URL for production
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Fallback to SQLite with warning
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    import warnings
    warnings.warn("No DATABASE_URL found, using SQLite. This is not recommended for production.")

# CORS Configuration - Restrictive for production
CORS_ALLOWED_ORIGINS = [
    "https://restyleproject-production.up.railway.app",
    "https://restyle-backend.onrender.com",
]

# Add any additional CORS origins from environment
additional_origins = os.environ.get('ADDITIONAL_CORS_ORIGINS', '')
if additional_origins:
    CORS_ALLOWED_ORIGINS.extend([origin.strip() for origin in additional_origins.split(',')])

CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_ALL_ORIGINS = False

# Security Settings for Production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Production logging - less verbose, focused on errors
LOGGING['root']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'

# Add Sentry for error monitoring in production
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(auto_enabling_integrations=False),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=os.environ.get('ENVIRONMENT', 'production'),
    )

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Cache configuration for production
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'