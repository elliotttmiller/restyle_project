# Deployment Guide

## Overview
Comprehensive guide for deploying Restyle.ai to production environments.

## 🎯 Pre-Deployment Checklist

### Security
- [ ] All secrets moved to environment variables
- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is strong and unique
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] HTTPS/SSL certificates configured
- [ ] CORS origins properly restricted
- [ ] Database credentials secured
- [ ] API keys rotated and secured
- [ ] Run `python manage.py check --deploy`

### Code Quality
- [ ] All tests passing
- [ ] Linting checks passed
- [ ] Security scan completed (bandit, safety)
- [ ] No hardcoded credentials
- [ ] Dependencies up to date
- [ ] Code reviewed and approved

### Infrastructure
- [ ] Database backed up
- [ ] Redis/Cache configured
- [ ] Static files configured
- [ ] Media storage configured (S3/CloudFront)
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Error tracking configured (Sentry)

## 🚀 Deployment Options

### Option 1: Railway.app (Current)

#### Initial Setup
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to project
railway link
```

#### Environment Variables
Set in Railway dashboard or via CLI:
```bash
railway variables set SECRET_KEY="your-secret-key"
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="yourdomain.railway.app"
railway variables set DATABASE_URL="postgresql://..."
railway variables set REDIS_URL="redis://..."

# AI Service Keys
railway variables set GOOGLE_API_KEY="..."
railway variables set AWS_ACCESS_KEY_ID="..."
railway variables set AWS_SECRET_ACCESS_KEY="..."
railway variables set EBAY_PRODUCTION_APP_ID="..."
```

#### Deploy
```bash
# Deploy to Railway
railway up

# Check logs
railway logs

# Check status
railway status
```

### Option 2: AWS Elastic Beanstalk

#### Setup
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p python-3.10 restyle-backend

# Create environment
eb create restyle-prod

# Deploy
eb deploy
```

#### Configuration (.ebextensions/django.config)
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: backend.wsgi:application
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: backend.settings
    DEBUG: "False"
```

### Option 3: Docker + AWS ECS

#### Build Docker Image
```bash
cd backend
docker build -t restyle-backend:latest .
docker tag restyle-backend:latest your-registry/restyle-backend:latest
docker push your-registry/restyle-backend:latest
```

#### ECS Task Definition (task-definition.json)
```json
{
  "family": "restyle-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-registry/restyle-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "False"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account-id:secret:secret-name"
        }
      ]
    }
  ]
}
```

### Option 4: Heroku

#### Setup
```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create restyle-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG="False"
```

#### Procfile
```
web: gunicorn backend.wsgi:application --log-file -
worker: celery -A backend worker -l info
beat: celery -A backend beat -l info
```

#### Deploy
```bash
git push heroku main
heroku ps:scale web=1 worker=1
heroku logs --tail
```

### Option 5: DigitalOcean App Platform

#### app.yaml
```yaml
name: restyle-backend
services:
  - name: web
    source_dir: backend
    github:
      repo: your-username/restyle_project
      branch: main
      deploy_on_push: true
    run_command: gunicorn backend.wsgi:application
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xs
    envs:
      - key: DEBUG
        value: "False"
      - key: SECRET_KEY
        value: ${SECRET_KEY}
        type: SECRET
databases:
  - name: restyle-db
    engine: PG
    version: "15"
```

## 🗄️ Database Setup

### PostgreSQL Production

#### Create Database
```sql
CREATE DATABASE restyle_production;
CREATE USER restyle_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE restyle_production TO restyle_user;
ALTER USER restyle_user CREATEDB;
```

#### Run Migrations
```bash
python manage.py migrate --no-input
python manage.py collectstatic --no-input
```

#### Create Superuser
```bash
python manage.py createsuperuser
```

### Database Backup Strategy

#### Automated Backups (PostgreSQL)
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="restyle_production"

pg_dump $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

#### Cron Job
```cron
0 2 * * * /path/to/backup.sh
```

## 📦 Static & Media Files

### AWS S3 Configuration

#### Install Dependencies
```bash
pip install boto3 django-storages
```

#### Settings Configuration
```python
# settings.py
if not DEBUG:
    # S3 Storage
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = 'us-east-1'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    
    # Static files
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

### CloudFront CDN
```python
AWS_S3_CUSTOM_DOMAIN = 'd123456789.cloudfront.net'
```

## 🔄 CI/CD Pipeline

### GitHub Actions (Automated Deployment)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway link ${{ secrets.RAILWAY_PROJECT_ID }}
          railway up --service backend
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### Blue-Green Deployment

```bash
# Deploy to staging first
railway up --service backend-staging

# Test staging
curl https://staging.yourdomain.com/api/health/

# Promote to production
railway promote backend-staging
```

## 📊 Monitoring & Logging

### Sentry Error Tracking

#### Install
```bash
pip install sentry-sdk
```

#### Configuration
```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
        environment='production',
    )
```

### CloudWatch Logs (AWS)

```python
# Install
pip install watchtower

# Configuration
LOGGING = {
    'handlers': {
        'cloudwatch': {
            'class': 'watchtower.CloudWatchLogHandler',
            'log_group': 'restyle-backend',
            'stream_name': 'production',
        },
    },
}
```

### New Relic APM

```bash
# Install
pip install newrelic

# Initialize
newrelic-admin generate-config LICENSE_KEY newrelic.ini

# Run with New Relic
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn backend.wsgi:application
```

## 🚨 Health Checks

### Kubernetes Liveness/Readiness Probes

```yaml
livenessProbe:
  httpGet:
    path: /api/health/
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/health/
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Load Balancer Health Check

```python
# views.py
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for load balancers"""
    try:
        # Check database
        from django.db import connection
        connection.ensure_connection()
        
        # Check Redis
        from django.core.cache import cache
        cache.set('health_check', 'ok', 1)
        
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e),
        }, status=500)
```

## 🔐 SSL/TLS Configuration

### Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📱 Mobile App Deployment

### Expo Application Services (EAS)

#### Setup
```bash
npm install -g eas-cli
eas login
eas build:configure
```

#### Build Configuration (eas.json)
```json
{
  "build": {
    "production": {
      "android": {
        "buildType": "apk"
      },
      "ios": {
        "simulator": false
      }
    }
  },
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json"
      },
      "ios": {
        "appleId": "your@email.com",
        "ascAppId": "1234567890"
      }
    }
  }
}
```

#### Build & Deploy
```bash
# Build
eas build --platform android --profile production
eas build --platform ios --profile production

# Submit to stores
eas submit --platform android
eas submit --platform ios
```

## 🔄 Rollback Procedure

### Quick Rollback

```bash
# Railway
railway rollback

# Heroku
heroku rollback

# Kubernetes
kubectl rollout undo deployment/restyle-backend

# Manual
git revert HEAD
git push origin main
```

## 📋 Post-Deployment

### Verification Steps
1. Check health endpoint: `curl https://yourdomain.com/api/health/`
2. Test authentication: Login and verify tokens work
3. Test image upload: Upload and analyze an image
4. Check error logs: Monitor for any errors
5. Test mobile app: Verify mobile can connect
6. Performance check: Run load tests
7. Security scan: Run vulnerability scan

### Monitoring
- Set up alerts for errors (>1% error rate)
- Monitor response times (>500ms)
- Track API usage and rate limits
- Monitor database performance
- Check cache hit rates

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [12-Factor App](https://12factor.net/)
- [AWS Best Practices](https://aws.amazon.com/architecture/well-architected/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
