# Re-Style Project - Collaborator Setup Guide

## 🚀 Quick Start (Recommended)

For new collaborators, simply run the automated setup script:

```bash
python setup_project.py
```

This will install all dependencies and create startup scripts automatically.

## 📋 Prerequisites

Before running the setup, ensure you have:

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 14+** - [Download here](https://nodejs.org/)
- **npm** - Usually comes with Node.js
- **Docker** (optional) - [Download here](https://www.docker.com/) for Redis

## 🔧 Manual Setup (Alternative)

If you prefer to set up components individually:

### 1. Backend Setup (Django)

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Optional: create admin user
```

### 2. Frontend Setup (React)

```bash
cd frontend
npm install
```

### 3. Mobile App Setup (React Native)

```bash
cd restyle-mobile
npm install
npm install -g @expo/cli  # Install Expo CLI globally
```

## 🚀 Starting the Application

### Option 1: Use the automated startup script
```bash
start_all.bat
```

### Option 2: Start services individually

**Terminal 1 - Backend:**
```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
celery -A backend worker -l info
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm start
```

**Terminal 4 - Mobile App:**
```bash
cd restyle-mobile
npx expo start
```

**Terminal 5 - Redis (if not using Docker):**
```bash
# Install Redis locally or use Docker:
docker run -d --name redis-restyle -p 6379:6379 redis:7-alpine
```

## 🌐 Access Points

Once all services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Mobile App**: Scan QR code with Expo Go app

## 📱 Mobile App Testing

1. Install **Expo Go** on your phone:
   - [Android](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - [iOS](https://apps.apple.com/app/expo-go/id982107779)

2. Scan the QR code displayed in the mobile terminal

## 🔧 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Node modules issues:**
```bash
# Clear npm cache
npm cache clean --force
# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Python virtual environment:**
```bash
# Create virtual environment
python -m venv venv
# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate
```

**Database issues:**
```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### Mobile App Issues

**Expo CLI not found:**
```bash
npm install -g @expo/cli
```

**Metro bundler issues:**
```bash
cd restyle-mobile
npx expo start --clear
```

## 📁 Project Structure

```
restyle_project/
├── backend/                 # Django backend
│   ├── requirements.txt     # Python dependencies
│   └── manage.py
├── frontend/               # React frontend
│   ├── package.json        # Node.js dependencies
│   └── src/
├── restyle-mobile/         # React Native mobile app
│   ├── package.json        # Node.js dependencies
│   └── app/
├── setup_project.py        # Automated setup script
├── start_all.bat          # Automated startup script
└── COLLABORATOR_SETUP.md  # This file
```

## 🔄 Development Workflow

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Update dependencies (if needed):**
   ```bash
   python setup_project.py
   ```

3. **Start development:**
   ```bash
   start_all.bat
   ```

## 📞 Getting Help

- Check the logs in each terminal for error messages
- Review `STARTUP_INSTRUCTIONS.md` for detailed setup info
- Check `debug.log` in the backend directory for Django errors

## 🎯 Next Steps

After setup, you can:

1. **Explore the codebase:**
   - Backend API endpoints in `backend/core/views.py`
   - Frontend components in `frontend/src/components/`
   - Mobile screens in `restyle-mobile/app/`

2. **Run tests:**
   ```bash
   cd backend && python manage.py test
   cd frontend && npm test
   ```

3. **Make changes and see them live:**
   - Frontend changes auto-reload at http://localhost:3000
   - Mobile changes auto-reload in Expo Go
   - Backend changes require server restart

Happy coding! 🚀 