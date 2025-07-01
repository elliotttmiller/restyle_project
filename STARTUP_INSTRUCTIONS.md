# Re-Style Application Startup Instructions

## 🚀 Quick Start with eBay Integration

### Prerequisites
- Python 3.8+
- Node.js 14+
- Docker (for Redis)
- eBay Developer Account with production credentials

### 1. Backend Setup with eBay Integration
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Create admin user

# Start Redis for Celery (required for eBay tasks)
docker run -d --name redis-ebay -p 6379:6379 redis:7-alpine

# Start Celery worker (in a new terminal)
celery -A backend worker -l info

# Start Django server
python manage.py runserver 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 3. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## 🔧 eBay Integration Features

### ✅ **Real eBay Listings**
- Creates actual live listings on eBay via Trading API
- Uses your Restyle_ai eBay account
- Automatically sets item details, pricing, and shipping

### ✅ **Real Market Analysis**
- Fetches actual sold items from eBay Browse API
- Analyzes comparable sales for accurate pricing
- Provides confidence scores based on data quality

### ✅ **Automated Task Processing**
- Celery worker processes eBay API calls asynchronously
- Real-time status updates for analysis and listings
- Error handling and retry logic

## 📋 API Endpoints

### Authentication
- `POST /api/token/` - Login
- `POST /api/users/register/` - Register

### Items & Analysis
- `GET /api/core/items/` - List items
- `POST /api/core/items/` - Create item
- `POST /api/core/items/{id}/analyze/` - Start market analysis
- `GET /api/core/items/{id}/analysis/` - Get analysis results

### Listings
- `POST /api/core/items/{id}/listings/` - Create eBay listing
- `GET /api/core/listings/` - List all listings

## 🧪 Testing eBay Integration

Run the test script to verify everything is working:
```bash
python test_ebay_integration.py
```

## 🔍 Troubleshooting

### eBay API Issues
1. Check your eBay credentials in `backend/backend/local_settings.py`
2. Verify your eBay app has the correct permissions
3. Check the debug logs in `backend/debug.log`

### Celery Issues
1. Ensure Redis is running: `docker ps | grep redis`
2. Check Celery worker logs for errors
3. Restart Celery worker if needed

### Database Issues
1. Run `python manage.py migrate`
2. Create superuser: `python manage.py createsuperuser`
3. Check database connection settings

## 📊 Monitoring

### Check Task Status
```bash
# Check Celery worker status
celery -A backend inspect active

# Check task results
celery -A backend inspect stats
```

### View Logs
```bash
# Django logs
tail -f backend/debug.log

# Celery worker logs (if running in terminal)
# Check the terminal where you started the Celery worker
```

## 🚨 Important Notes

1. **eBay Production Environment**: The app is configured to use eBay's production environment, not sandbox
2. **Real Listings**: Creating a listing will post a real item on eBay under your Restyle_ai account
3. **API Limits**: eBay has rate limits - the app includes proper error handling
4. **PayPal Email**: Update the PayPal email in `backend/core/tasks.py` before creating listings

## 🔄 Recent Updates

✅ **Fixed Issues:**
- Real eBay API integration for listings and analysis
- Proper Celery task processing
- Real-time analysis status updates
- Error handling and logging
- Frontend polling for analysis updates

## Docker Setup (Alternative)

```bash
docker-compose up -d
```

## Fixed Issues

✅ **Analysis Endpoint**: Added missing `/core/items/{id}/analyze/` endpoint
✅ **Error Handling**: Improved authentication error handling in ItemList
✅ **Celery Configuration**: Fixed Celery app name
✅ **Dockerfile**: Fixed Django command in Dockerfile

## Common Issues & Solutions

### Dashboard Not Loading
1. Ensure you're logged in (check localStorage for auth token)
2. Check browser console for API errors
3. Verify backend is running on port 8000

### Authentication Issues
1. Clear browser localStorage
2. Try logging in again
3. Check backend logs for authentication errors

### Database Issues
1. Run `python manage.py migrate`
2. Create superuser: `python manage.py createsuperuser`
3. Check database connection settings

## API Endpoints

- `POST /api/token/` - Login
- `POST /api/users/register/` - Register
- `GET /api/core/items/` - List items
- `POST /api/core/items/` - Create item
- `POST /api/core/items/{id}/analyze/` - Run analysis 