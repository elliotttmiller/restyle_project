# Restyle.ai - AI-Powered Fashion Search Platform

A comprehensive full-stack application that uses advanced AI to analyze fashion items through images and provide intelligent market search results via eBay integration.

## 🚀 Project Overview

Restyle.ai combines computer vision, natural language processing, and market intelligence to help users find similar fashion items by simply taking or uploading photos. The platform leverages multiple AI services including Google Vision API, AWS Rekognition, and CLIP models for sophisticated image analysis.

## 🏗️ Architecture

### Backend (Django REST API)
- **Framework**: Django 4.2.13 with Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Task Queue**: Celery with Redis
- **Deployment**: Railway.app with Docker support

### Mobile App (React Native + Expo)
- **Framework**: React Native with Expo SDK 53
- **Navigation**: Expo Router
- **State Management**: Zustand
- **Image Handling**: Expo Image Picker

### Frontend (React Web - Optional)
- **Framework**: React.js
- **Styling**: CSS with custom themes
- **API Integration**: Axios

## 🤖 AI Services Integration

### Multi-Modal AI Pipeline
1. **Google Vision API** - Object detection and OCR
2. **AWS Rekognition** - Advanced image analysis and labeling
3. **CLIP Models** - Semantic image-text understanding
4. **FAISS** - Fast similarity search with vector embeddings
5. **Custom NLP** - Query enhancement and attribute extraction

### Key AI Features
- **Object Detection**: Identifies fashion items in images
- **Attribute Extraction**: Determines color, style, brand, category
- **Semantic Search**: CLIP-based visual similarity matching
- **Market Intelligence**: eBay API integration for real-time pricing
- **Multi-Expert System**: Combines multiple AI models for accuracy

## 📱 Features

### Mobile App
- **Camera Integration**: Take photos for instant AI analysis
- **Image Upload**: Select from photo library
- **Real-time Search**: AI-powered eBay marketplace search
- **User Authentication**: Secure login/registration
- **Search History**: Track previous searches
- **Responsive UI**: Optimized for iOS and Android

### Backend API
- **Image Analysis Endpoints**: `/api/analyze-image/`
- **Search Endpoints**: `/api/search/`
- **User Management**: Authentication and profiles
- **Market Data**: eBay integration with real-time pricing
- **Caching**: Redis-based performance optimization

## 🛠️ Technology Stack

### Backend Dependencies
```
Django==4.2.13
djangorestframework==3.15.1
torch & torchvision (PyTorch)
transformers & sentence-transformers
google-cloud-vision==3.10.2
boto3==1.39.4 (AWS SDK)
faiss-cpu==1.11.0
celery==5.3.6
redis==5.0.1
pillow==11.3.0
ebaysdk==2.2.0
```

### Mobile Dependencies
```
expo: 53.0.19
react-native: 0.79.5
expo-router: ~5.1.3
expo-image-picker: ~16.1.4
axios: ^1.10.0
zustand: ^5.0.6
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Redis server
- Google Cloud account with Vision API enabled
- AWS account with Rekognition access
- eBay Developer account

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

### Mobile App Setup
```bash
cd restyle-mobile
npm install
npx expo start
```

### Environment Configuration
Create `.env` file with:
```env
# Google Cloud
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CLOUD_PROJECT_ID=your_project_id

# AWS
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=us-east-1

# eBay
EBAY_PRODUCTION_APP_ID=your_ebay_app_id
EBAY_PRODUCTION_CLIENT_SECRET=your_ebay_secret
EBAY_PRODUCTION_REFRESH_TOKEN=your_refresh_token

# Database
DATABASE_URL=your_postgres_url
REDIS_URL=your_redis_url
```

## 📁 Project Structure

```
restyle_project/
├── backend/                 # Django REST API
│   ├── core/               # Main app with AI services
│   │   ├── ai_service.py          # Primary AI orchestration
│   │   ├── advanced_ai_service.py # AWS Rekognition integration
│   │   ├── models.py              # Database models
│   │   ├── views.py               # API endpoints
│   │   └── serializers.py         # API serializers
│   ├── users/              # User management
│   └── backend/            # Django settings
├── restyle-mobile/         # React Native mobile app
│   ├── app/               # Expo Router pages
│   │   ├── (app)/         # Main app screens
│   │   │   └── dashboard.js       # Main search interface
│   │   └── (auth)/        # Authentication screens
│   └── shared/            # Shared utilities
├── frontend/              # React web app (optional)
├── test_files/           # Comprehensive test suite
└── readme_files/         # Documentation
```

## 🔧 Recent Fixes & Improvements

### Backend AI Logic Bug Fix
- **Issue**: Incorrect AWS Rekognition API usage causing "no results found"
- **Fix**: Changed from `RecognizeCelebrities` to `detect_labels` for general object detection
- **File**: `backend/core/advanced_ai_service.py`

### Frontend Dashboard Completion
- **Issue**: Truncated dashboard.js file missing critical functionality
- **Fix**: Completed full image search functionality with camera integration
- **File**: `restyle-mobile/app/(app)/dashboard.js`

### Code Quality Improvements
- **Issue**: Multiple Pylance and Sourcery warnings
- **Fix**: Resolved structural errors, datetime usage, and redundant conditionals
- **File**: `backend/core/ai_service.py`

## 🧪 Testing

### Comprehensive Test Suite
```bash
# Backend tests
cd backend
python comprehensive_test_suite.py

# Mobile connection tests
cd restyle-mobile
node test_railway_connection.js
```

### Test Coverage
- AI service integration tests
- eBay API functionality tests
- Image processing pipeline tests
- Authentication flow tests
- Mobile-backend connectivity tests

## 🚀 Deployment

### Railway.app (Current)
- Automatic deployments from GitHub
- PostgreSQL database included
- Redis addon for caching
- Environment variables configured

### Docker Support
```bash
docker-compose up --build
```

## 📊 Performance Optimizations

### FAISS Vector Search
- Fast similarity search with pre-built indexes
- Reduced search time from seconds to milliseconds
- Automatic index rebuilding for new items

### Caching Strategy
- Redis caching for frequent API calls
- Image analysis result caching
- eBay search result caching

### Multi-Expert AI System
- Parallel processing of multiple AI models
- Confidence scoring and result fusion
- Fallback mechanisms for service failures

## 🔐 Security Features

- JWT authentication (configurable)
- CORS configuration for mobile app
- Environment variable protection
- API rate limiting
- Secure credential management

## 📈 Monitoring & Analytics

### Logging System
- Comprehensive debug logging
- AI service performance tracking
- Error tracking and reporting
- Search analytics and insights

### Health Checks
- Service availability monitoring
- Database connection checks
- External API status verification

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support & Documentation

## 📚 Backend API Endpoints

Below is a comprehensive list of backend API endpoints provided by the Django REST API. All endpoints are available under `/api/core/` (and `/core/` for mobile compatibility), unless otherwise noted.

### Health & Status
- `GET /api/core/health/` — Basic health check for the core service
- `GET /api/core/health-check/` — Authenticated health check (requires login)
- `GET /api/core/ai/status/` — AI service status (Google Vision, AWS Rekognition, Gemini, etc.)
- `GET /api/core/metrics/` — System performance metrics (CPU, memory, disk)
- `GET /api/core/` — Root endpoint with status and available endpoints

### eBay OAuth & Token Management
- `GET /api/core/ebay-oauth/` — Initiate eBay OAuth flow
- `GET /api/core/ebay-oauth-callback/` — eBay OAuth callback (handles code/token exchange)
- `GET /api/core/ebay-oauth-declined/` — eBay OAuth declined/cancelled endpoint
- `GET /api/core/ebay-token/health/` — eBay OAuth token status
- `POST /api/core/ebay-token/action/` — eBay token action endpoint (placeholder)
- `POST /api/core/admin/set-ebay-refresh-token/` — Set eBay refresh token (admin only)

### Item & Listing Management
- `GET/POST /api/core/items/` — List or create items
- `GET /api/core/items/<pk>/` — Retrieve item details
- `POST /api/core/items/<pk>/analyze/` — Trigger market analysis for an item
- `GET /api/core/items/<pk>/analysis/` — Get analysis status for an item
- `GET/POST /api/core/items/<item_pk>/listings/` — List or create listings for an item
- `GET /api/core/listings/<pk>/` — Retrieve listing details

### AI & Image Analysis
- `POST /api/core/ai/image-search/` — AI-powered image search
- `POST /api/core/ai/advanced-search/` — Advanced multi-expert AI image search
- `POST /api/core/ai/crop-preview/` — Crop preview (AI-based, placeholder)

### Price Analysis
- `POST /api/core/price-analysis/` — Price analysis for a given item/image

### Legal & Policy
- `GET /api/core/privacy-policy/` — Privacy policy endpoint
- `GET /api/core/accepted/` — Accepted endpoint (legal/consent)
- `GET /api/core/declined/` — Declined endpoint (legal/consent)

### Test & Utility
- `GET /api/core/test-ebay-login/` — Test eBay login endpoint

### Admin & Auth (global)
- `GET /admin/` — Django admin panel
- `POST /api/token/` — Obtain JWT token (login)
- `POST /api/token/refresh/` — Refresh JWT token
- `GET /api/test-credentials/` — Test credentials endpoint
- `GET /api/protected/` — Protected endpoint (requires authentication)
- `GET /api/profile/` — Get user profile (requires authentication)

**Note:** All endpoints return JSON responses. Some endpoints require authentication or admin privileges. For full details, see the code in `backend/core/views.py` and `backend/core/urls.py`.

### Additional Documentation
- [Credential Setup Guide](readme_files/CREDENTIAL_SETUP_GUIDE.md)
- [eBay OAuth Setup](readme_files/EBAY_OAUTH_SETUP.md)
- [AWS Rekognition Setup](readme_files/AMAZON_REKOGNITION_SETUP.md)
- [Multi-Expert AI Implementation](readme_files/MULTI_EXPERT_AI_IMPLEMENTATION.md)

### Troubleshooting
- Check logs in `backend/debug.log`
- Verify environment variables are set
- Ensure all services are running (Redis, PostgreSQL)
- Test API endpoints with provided test scripts

## 🎯 Roadmap

### Upcoming Features
- [ ] Advanced filtering and sorting
- [ ] Price tracking and alerts
- [ ] Social features and sharing
- [ ] Machine learning model improvements
- [ ] Additional marketplace integrations
- [ ] Web app completion
- [ ] iOS/Android app store deployment

---

**Current Status**: ✅ Fully functional with recent bug fixes and improvements
**Last Updated**: January 2025
**Version**: 1.0.0