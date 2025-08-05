# Production Deployment Checklist

## Pre-Deployment Security Checklist

### Environment Variables (CRITICAL)
- [ ] `SECRET_KEY` - Generate new secret key for production
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `DJANGO_SETTINGS_MODULE=backend.settings.prod`
- [ ] `DEBUG=false` (or omit entirely)
- [ ] `ALLOWED_HOSTS` - Comma-separated list of production domains
- [ ] `REDIS_URL` - For Celery and caching (if using Redis)

### API Keys and Credentials
- [ ] `EBAY_PRODUCTION_APP_ID`
- [ ] `EBAY_PRODUCTION_CERT_ID` 
- [ ] `EBAY_PRODUCTION_CLIENT_SECRET`
- [ ] `EBAY_PRODUCTION_REFRESH_TOKEN`
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account JSON
- [ ] `GOOGLE_CLOUD_PROJECT`
- [ ] `SENTRY_DSN` - For error monitoring (recommended)

### Email Configuration (Optional)
- [ ] `EMAIL_HOST_USER`
- [ ] `EMAIL_HOST_PASSWORD`
- [ ] `DEFAULT_FROM_EMAIL`

## Railway Deployment

### 1. Repository Setup
- [ ] Code pushed to GitHub
- [ ] Repository connected to Railway

### 2. Environment Configuration
- [ ] All required environment variables set in Railway dashboard
- [ ] PostgreSQL service added and DATABASE_URL configured
- [ ] Redis service added (if using Celery)

### 3. Deployment Settings
- [ ] Build root set to `backend` directory
- [ ] Procfile configured correctly
- [ ] railway.json present with correct settings

### 4. Post-Deployment Verification
- [ ] Health check: `https://yourdomain.com/health/`
- [ ] Admin access: `https://yourdomain.com/admin/`
- [ ] Static files loading correctly
- [ ] No security warnings in logs

## Render Deployment

### 1. Service Creation
- [ ] New Web Service created
- [ ] GitHub repository selected
- [ ] Root directory set to `backend`

### 2. Build Settings
```bash
# Build Command:
pip install -r requirements.txt

# Start Command:
python manage.py migrate && python manage.py create_prod_superuser && python manage.py collectstatic --noinput && gunicorn backend.wsgi:application
```

### 3. Environment Variables
- [ ] All production environment variables configured
- [ ] PostgreSQL database service connected

## Security Verification

### SSL/HTTPS
- [ ] HTTPS enforced (SECURE_SSL_REDIRECT=True in prod settings)
- [ ] HSTS headers configured
- [ ] Secure cookies enabled

### Headers Security
- [ ] X-Frame-Options: DENY
- [ ] X-Content-Type-Options: nosniff
- [ ] X-XSS-Protection enabled

### CORS Configuration
- [ ] Only production domains in CORS_ALLOWED_ORIGINS
- [ ] CORS_ALLOW_ALL_ORIGINS=False in production

## Monitoring Setup

### Sentry (Recommended)
- [ ] Sentry project created
- [ ] SENTRY_DSN environment variable set
- [ ] Error alerts configured

### Logging
- [ ] Application logs accessible
- [ ] Error logs monitored
- [ ] Performance metrics tracked

## Database

### PostgreSQL
- [ ] Production database created
- [ ] Migrations applied successfully
- [ ] Admin user created
- [ ] Database backups configured

## Performance

### Static Files
- [ ] WhiteNoise configured for static file serving
- [ ] Static files collected successfully
- [ ] CDN configured (optional)

### Caching
- [ ] Redis configured for caching (optional)
- [ ] Session caching enabled (optional)

## Testing

### Functional Tests
- [ ] Health endpoint returns 200 OK
- [ ] Admin login works
- [ ] API endpoints respond correctly
- [ ] Authentication flow works

### Load Testing (Optional)
- [ ] Performance under expected load tested
- [ ] Database connection limits verified
- [ ] Memory usage monitored

## Rollback Plan

### Emergency Procedures
- [ ] Previous deployment version identified
- [ ] Rollback procedure documented
- [ ] Database migration rollback plan
- [ ] Contact information for team members

## Post-Deployment

### 24-Hour Monitoring
- [ ] Error rates monitored
- [ ] Performance metrics checked
- [ ] User feedback collected
- [ ] Security logs reviewed

### Documentation Updates
- [ ] Deployment documentation updated
- [ ] Environment variables documented
- [ ] Troubleshooting guide updated

---

## Quick Commands

### Generate SECRET_KEY
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Test Production Settings Locally
```bash
export DJANGO_SETTINGS_MODULE=backend.settings.prod
export SECRET_KEY="your-secret-key"
export DATABASE_URL="sqlite:///test.db"
export DEBUG=false
python manage.py check --deploy
```

### Health Check
```bash
curl -I https://yourdomain.com/health/
```

### Admin Test
```bash
curl -u elliotttmiller:elliott https://yourdomain.com/admin/
```