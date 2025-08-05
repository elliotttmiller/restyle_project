"""
Development settings for backend project.
"""

from .base import *

# Override base settings for development
DEBUG = True

# Development SECRET_KEY (only if not set in environment)
if not os.environ.get('SECRET_KEY'):
    SECRET_KEY = 'django-insecure-dev-key-only-for-local-development'

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Database - Use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS Configuration - More permissive for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8081",  # Expo development server
    "http://127.0.0.1:8081",
    "exp://localhost:8081",
    "exp://127.0.0.1:8081",
]

# Allow local IPs for mobile development
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://192\.168\.\d{1,3}\.\d{1,3}:(3000|8000|8081)$",
    r"^exp://192\.168\.\d{1,3}\.\d{1,3}:8081$",
]

CORS_ALLOW_ALL_HEADERS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # Only for development

# Disable security features in development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Add debug toolbar in development (if installed)
try:
    import debug_toolbar
    INSTALLED_APPS = ['debug_toolbar'] + INSTALLED_APPS
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
except ImportError:
    pass

# Development logging - more verbose
LOGGING['handlers']['file'] = {
    'class': 'logging.FileHandler',
    'filename': str(BASE_DIR / 'debug.log'),
    'formatter': 'verbose',
    'mode': 'a',
    'encoding': 'utf-8',
}

LOGGING['root']['handlers'].append('file')
LOGGING['root']['level'] = 'DEBUG'

# Add detailed logging for development
LOGGING['loggers'].update({
    'core.ai_service': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'core.vertex_ai_service': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
        'propagate': False,
    },
    'django.db.backends': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    },
})

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'