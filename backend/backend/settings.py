"""
DEPRECATED: This settings file is deprecated.
Please use environment-specific settings:
- backend.settings.dev for development
- backend.settings.prod for production

This file is kept for backward compatibility only.
"""

import os
import warnings

# Issue deprecation warning
warnings.warn(
    "backend.settings is deprecated. Use backend.settings.dev or backend.settings.prod instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import development settings by default for backward compatibility
# Set DJANGO_SETTINGS_MODULE=backend.settings.prod for production
if os.environ.get('DEBUG', 'False').lower() == 'true':
    from .settings.dev import *
else:
    from .settings.prod import *