# eBay OAuth Token Refresh System

This document describes the automated eBay OAuth token refresh system implemented in your application.

## Overview

The token refresh system provides:
- **Automatic token renewal** before expiration
- **Fallback mechanisms** when refresh fails
- **Caching** for performance
- **Monitoring and alerting** for token health
- **Management commands** for manual operations

## Architecture

### Components

1. **`ebay_auth.py`** - Core token management service
2. **`tasks.py`** - Celery tasks for automated refresh
3. **`views.py`** - Updated to use new token manager
4. **Management commands** - Manual token operations
5. **Configuration** - Settings for token behavior

### Token Flow

```
Application Request → Token Manager → Check Cache → Valid Token?
                                                    ↓
                                              No → Refresh Token → Success?
                                                    ↓
                                              Yes → Use Token
                                                    ↓
                                              No → Fallback Token
```

## Configuration

### Required Settings

Add these to your `local_settings.py`:

```python
# eBay OAuth Configuration
EBAY_PRODUCTION_APP_ID = "your-app-id"
EBAY_PRODUCTION_CERT_ID = "your-cert-id"
EBAY_PRODUCTION_CLIENT_SECRET = "your-client-secret"
EBAY_PRODUCTION_REFRESH_TOKEN = "your-refresh-token"
EBAY_PRODUCTION_USER_TOKEN = "your-user-token"  # Fallback
```

### Optional Settings

```python
# Token refresh behavior
EBAY_TOKEN_REFRESH_ENABLED = True
EBAY_TOKEN_REFRESH_BUFFER_HOURS = 1
EBAY_TOKEN_CACHE_TIMEOUT = 7200

# Celery scheduling
EBAY_TOKEN_REFRESH_INTERVAL = 3600  # 1 hour
EBAY_TOKEN_VALIDATION_INTERVAL = 1800  # 30 minutes
```

## Usage

### Automatic Usage

The system automatically handles token refresh in your existing code:

```python
# In your views or tasks
from core.ebay_auth import get_ebay_oauth_token

token = get_ebay_oauth_token()  # Automatically refreshed if needed
```

### Manual Operations

#### Management Commands

```bash
# Check token status
python manage.py manage_ebay_tokens status

# Force refresh token
python manage.py manage_ebay_tokens force-refresh

# Validate current token
python manage.py manage_ebay_tokens validate

# Refresh token (if needed)
python manage.py manage_ebay_tokens refresh
```

#### Programmatic Operations

```python
from core.ebay_auth import token_manager, validate_ebay_token

# Force refresh
new_token = token_manager.force_refresh()

# Validate token
is_valid = validate_ebay_token(token)

# Get token with automatic refresh
token = token_manager.get_valid_token()
```

### Celery Tasks

The system includes Celery tasks for automated operations:

```python
from core.tasks import refresh_ebay_token_task, validate_ebay_token_task

# Schedule periodic refresh
refresh_ebay_token_task.delay()

# Validate token health
validate_ebay_token_task.delay()
```

## Testing

### Run the Test Suite

```bash
python test_token_refresh_system.py
```

### Individual Tests

```bash
# Test new token
python test_new_token.py

# Test search functionality
python test_search_with_auth.py

# Test direct API
python test_ebay_browse_api.py
```

## Monitoring

### Logs

The system logs all token operations:

```
INFO - Successfully refreshed eBay OAuth token, expires at 2024-01-15 10:30:00
WARNING - eBay OAuth token expired or expiring soon, refreshing...
ERROR - Failed to refresh eBay token: 401 - Invalid refresh token
```

### Health Checks

Monitor token health with:

```python
from core.ebay_auth import validate_ebay_token

# Check if token is valid
is_healthy = validate_ebay_token(token)
```

## Troubleshooting

### Common Issues

1. **Token Expired**
   - Run: `python manage.py manage_ebay_tokens force-refresh`
   - Check refresh token in settings

2. **Refresh Failed**
   - Verify credentials in settings
   - Check network connectivity
   - Review eBay API documentation

3. **Cache Issues**
   - Clear cache: `python manage.py manage_ebay_tokens force-refresh`
   - Check Redis connection

### Debug Mode

Enable debug logging:

```python
# In settings
LOGGING = {
    'loggers': {
        'core.ebay_auth': {
            'level': 'DEBUG',
        },
    },
}
```

## Security Considerations

1. **Store credentials securely** - Use environment variables in production
2. **Rotate refresh tokens** - Update periodically
3. **Monitor access** - Log token usage
4. **Limit permissions** - Use minimal required scopes

## Migration Guide

### From Manual Token Management

1. **Update imports**:
   ```python
   # Old
   from django.conf import settings
   token = getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None)
   
   # New
   from core.ebay_auth import get_ebay_oauth_token
   token = get_ebay_oauth_token()
   ```

2. **Add configuration** to `local_settings.py`

3. **Test the system** with provided test scripts

4. **Monitor logs** for any issues

### Backward Compatibility

The system maintains backward compatibility:
- Falls back to settings token if refresh fails
- Existing code continues to work
- Gradual migration possible

## Best Practices

1. **Set up monitoring** - Monitor token health regularly
2. **Use Celery tasks** - Schedule automatic refresh
3. **Handle errors gracefully** - Implement fallback mechanisms
4. **Test thoroughly** - Use provided test suite
5. **Document changes** - Keep configuration updated

## Support

For issues or questions:
1. Check the logs for error messages
2. Run the test suite to identify problems
3. Verify configuration settings
4. Review eBay API documentation

## Future Enhancements

Potential improvements:
- **Database storage** for tokens
- **Multiple account support**
- **Advanced monitoring dashboard**
- **Webhook integration** for token events
- **Rate limiting** for refresh operations 