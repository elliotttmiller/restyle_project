#!/usr/bin/env python3
"""
Re-Style Project Setup Script
Automatically installs all dependencies for backend, frontend, and mobile app.
Run this script to set up the entire project for development.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, cwd=cwd, shell=shell, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error running: {command}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Exception running: {command}")
        print(f"Error: {e}")
        return False

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    try:
        python_version = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python: {python_version.stdout.strip()}")
    except:
        print("❌ Python not found. Please install Python 3.8+")
        return False
    
    # Check Node.js
    try:
        node_version = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✅ Node.js: {node_version.stdout.strip()}")
    except:
        print("❌ Node.js not found. Please install Node.js 14+")
        return False
    
    # Check npm
    try:
        npm_version = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        print(f"✅ npm: {npm_version.stdout.strip()}")
    except:
        print("❌ npm not found. Please install npm")
        return False
    
    # Check Docker (optional but recommended for Redis)
    try:
        docker_version = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        print(f"✅ Docker: {docker_version.stdout.strip()}")
    except:
        print("⚠️  Docker not found. Redis will need to be installed separately")
    
    return True

def setup_backend():
    """Setup Django backend"""
    print("\n🐍 Setting up Django backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Install Python dependencies
    print("📦 Installing Python dependencies...")
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", cwd="backend"):
        return False
    
    # Run migrations
    print("🗄️  Running database migrations...")
    if not run_command(f"{sys.executable} manage.py migrate", cwd="backend"):
        return False
    
    # Create superuser (optional)
    print("👤 Creating superuser (optional - press Ctrl+C to skip)...")
    try:
        run_command(f"{sys.executable} manage.py createsuperuser", cwd="backend")
    except KeyboardInterrupt:
        print("⏭️  Skipping superuser creation")
    
    print("✅ Backend setup complete!")
    return True

def setup_frontend():
    """Setup React frontend"""
    print("\n⚛️  Setting up React frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install Node.js dependencies
    print("📦 Installing Node.js dependencies...")
    if not run_command("npm install", cwd="frontend"):
        return False
    
    print("✅ Frontend setup complete!")
    return True

def setup_mobile():
    """Setup React Native mobile app"""
    print("\n📱 Setting up React Native mobile app...")
    
    mobile_dir = Path("restyle-mobile")
    if not mobile_dir.exists():
        print("❌ Mobile app directory not found")
        return False
    
    # Install Node.js dependencies
    print("📦 Installing Node.js dependencies...")
    if not run_command("npm install", cwd="restyle-mobile"):
        return False
    
    # Install Expo CLI globally if not already installed
    print("📱 Installing Expo CLI...")
    run_command("npm install -g @expo/cli")
    
    print("✅ Mobile app setup complete!")
    return True

def create_startup_scripts():
    """Create convenient startup scripts"""
    print("\n🚀 Creating startup scripts...")
    
    # Create a comprehensive startup script
    startup_script = """@echo off
echo Starting Re-Style Application...
echo.

echo Starting Redis (if Docker is available)...
docker run -d --name redis-restyle -p 6379:6379 redis:7-alpine 2>nul || echo Redis container already running or Docker not available

echo Starting Django backend...
start cmd /k "cd backend && python manage.py runserver 0.0.0.0:8000"

echo Starting Celery worker...
start cmd /k "cd backend && celery -A backend worker -l info"

echo Starting React frontend...
start cmd /k "cd frontend && npm start"

echo Starting mobile app...
start cmd /k "cd restyle-mobile && npx expo start"

echo.
echo 🎉 All services are starting up!
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo Admin Panel: http://localhost:8000/admin
echo Mobile App: Scan QR code in the mobile terminal
echo.
pause
"""
    
    with open("start_all.bat", "w") as f:
        f.write(startup_script)
    
    print("✅ Created start_all.bat")
    return True

def main():
    """Main setup function"""
    print("🚀 Re-Style Project Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install the missing tools.")
        return
    
    # Setup each component
    success = True
    
    if not setup_backend():
        success = False
    
    if not setup_frontend():
        success = False
    
    if not setup_mobile():
        success = False
    
    if not create_startup_scripts():
        success = False
    
    if success:
        print("\n🎉 Setup complete!")
        print("\n📋 Next steps:")
        print("1. Run 'start_all.bat' to start all services")
        print("2. Or start services individually:")
        print("   - Backend: cd backend && python manage.py runserver")
        print("   - Frontend: cd frontend && npm start")
        print("   - Mobile: cd restyle-mobile && npx expo start")
        print("   - Celery: cd backend && celery -A backend worker")
        print("\n🌐 Access points:")
        print("- Frontend: http://localhost:3000")
        print("- Backend API: http://localhost:8000")
        print("- Admin Panel: http://localhost:8000/admin")
        print("- Mobile: Scan QR code with Expo Go")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main() 