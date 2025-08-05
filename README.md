# Re-Style Project - Django Backend

A production-ready Django REST API backend for the Re-Style fashion recommendation application.

## Features

- **Secure Authentication**: JWT-based authentication with session support
- **User Management**: Custom user model with profile management
- **AI Integration**: Fashion recommendation AI services
- **eBay Integration**: Product search and recommendation from eBay
- **Health Monitoring**: Built-in health checks and error monitoring
- **Production Ready**: Configured for deployment on Railway, Render, and other platforms

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- Redis (for Celery tasks and caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/elliotttmiller/restyle_project.git
   cd restyle_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.template .env
   # Edit .env with your configuration (see Environment Variables section)
   ```

5. **Run migrations**
   ```bash
   cd backend
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py create_prod_superuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000`

## Environment Variables

### Required

- `SECRET_KEY`: Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DATABASE_URL`: PostgreSQL database URL (format: `postgres://user:password@host:port/dbname`)

### Optional

- `DEBUG`: Set to `true` for development (default: `false`)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `REDIS_URL`: Redis URL for Celery and caching
- `SENTRY_DSN`: Sentry DSN for error monitoring
- `EMAIL_HOST_USER`: SMTP email username
- `EMAIL_HOST_PASSWORD`: SMTP email password

### API Keys

- `EBAY_PRODUCTION_APP_ID`: eBay API application ID
- `EBAY_PRODUCTION_CERT_ID`: eBay API certificate ID
- `EBAY_PRODUCTION_CLIENT_SECRET`: eBay API client secret
- `EBAY_PRODUCTION_REFRESH_TOKEN`: eBay API refresh token
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google Cloud service account JSON
- `GOOGLE_CLOUD_PROJECT`: Google Cloud project ID

## API Endpoints

### Health Check
- `GET /health/` - Returns server health status
- `GET /` - Root endpoint with basic server info

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/users/register/` - User registration
- `GET /api/profile/` - Get user profile (authenticated)

### Admin
- `/admin/` - Django admin interface

## Development

### Settings

The project uses environment-specific settings:

- `backend.settings.dev` - Development settings
- `backend.settings.prod` - Production settings
- `backend.settings.base` - Base settings (shared)

Set `DJANGO_SETTINGS_MODULE` environment variable to specify which settings to use:

```bash
# Development (default)
export DJANGO_SETTINGS_MODULE=backend.settings.dev

# Production
export DJANGO_SETTINGS_MODULE=backend.settings.prod
```

### Code Quality

The project includes linting and formatting tools:

```bash
# Format code with Black
black .

# Check code style with flake8
flake8

# Sort imports with isort
isort .

# Run all checks
black . && isort . && flake8
```

### Testing

```bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test backend.tests.HealthEndpointTests

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Database

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py create_prod_superuser
```

## Deployment

### Railway

1. **Connect your GitHub repository to Railway**

2. **Set environment variables in Railway dashboard:**
   - `SECRET_KEY`
   - `DATABASE_URL` (provided by Railway PostgreSQL service)
   - `DJANGO_SETTINGS_MODULE=backend.settings.prod`
   - Add any API keys needed

3. **Deploy:**
   Railway will automatically deploy on git push using the `Procfile`.

### Render

1. **Create a new Web Service on Render**

2. **Set build command:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set start command:**
   ```bash
   cd backend && python manage.py migrate && python manage.py create_prod_superuser && python manage.py collectstatic --noinput && gunicorn backend.wsgi:application
   ```

4. **Set environment variables:**
   Same as Railway setup above.

### Docker

```bash
# Build image
docker build -t restyle-backend .

# Run container
docker run -p 8000:8000 --env-file .env restyle-backend
```

## Architecture

### Project Structure

```
backend/
├── backend/                 # Django project settings
│   ├── settings/           # Environment-specific settings
│   │   ├── __init__.py
│   │   ├── base.py        # Base settings
│   │   ├── dev.py         # Development settings
│   │   └── prod.py        # Production settings
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI application
│   └── tests.py           # Backend tests
├── users/                  # User management app
├── core/                   # Core business logic app
├── manage.py              # Django management script
├── Procfile               # Railway/Heroku deployment
└── railway_start.sh       # Startup script
```

### Security Features

- Environment-based secret key management
- HTTPS enforcement in production
- Secure cookie settings
- CORS configuration
- CSRF protection
- SQL injection protection (Django ORM)
- XSS protection headers

## Troubleshooting

### Common Issues

1. **"SECRET_KEY environment variable is required"**
   - Ensure SECRET_KEY is set in your environment or .env file

2. **Database connection errors**
   - Check DATABASE_URL format: `postgres://user:password@host:port/dbname`
   - Ensure PostgreSQL service is running

3. **Static files not loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_ROOT and STATIC_URL settings

4. **CORS errors in development**
   - Ensure frontend URL is in CORS_ALLOWED_ORIGINS
   - Check that corsheaders is installed and configured

5. **Admin user creation fails**
   - Check that users app migrations have been applied
   - Verify CustomUser model is properly configured

### Debug Mode

Enable debug mode for development:

```bash
export DEBUG=true
export DJANGO_SETTINGS_MODULE=backend.settings.dev
```

### Logs

Check application logs:

```bash
# Railway
railway logs

# Local development
tail -f backend/debug.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact: elliotttmiller@example.com

---

## API Documentation

### Authentication Flow

1. **Register a new user:**
   ```bash
   curl -X POST http://localhost:8000/api/users/register/ \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "securepassword123"}'
   ```

2. **Login to get tokens:**
   ```bash
   curl -X POST http://localhost:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "securepassword123"}'
   ```

3. **Use token for authenticated requests:**
   ```bash
   curl -X GET http://localhost:8000/api/profile/ \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

### Health Check

```bash
curl http://localhost:8000/health/
```

Response:
```json
{
  "status": "healthy",
  "service": "restyle-backend",
  "timestamp": "2024-01-01T00:00:00Z"
}
```