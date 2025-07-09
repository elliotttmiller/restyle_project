#!/usr/bin/env python3
"""
Re-Style Application Startup Script (Fixed for Windows)
This script starts the entire Re-Style application including:
- Docker services (backend, frontend, Redis, Celery)
- Database setup and migrations
- Frontend build and server
- Health checks
"""

import os
import sys
import time
import subprocess
import requests
import json
from pathlib import Path

def run_command(command, description, check=True, shell=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=shell, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            return e
        return e

def wait_for_service(url, service_name, max_attempts=30):
    """Wait for a service to be ready"""
    print(f"\n⏳ Waiting for {service_name} to be ready...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Attempt {attempt + 1}/{max_attempts} - {service_name} not ready yet...")
        time.sleep(2)
    
    print(f"❌ {service_name} failed to start within {max_attempts * 2} seconds")
    return False

def check_docker():
    """Check if Docker is running"""
    print("\n🔍 Checking Docker status...")
    try:
        result = subprocess.run("docker --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker is available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker is not available")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False

def check_docker_compose():
    """Check if Docker Compose is available"""
    print("\n🔍 Checking Docker Compose status...")
    try:
        result = subprocess.run("docker-compose --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose is available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker Compose is not available")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker Compose: {e}")
        return False

def setup_frontend():
    """Setup and start the frontend"""
    print("\n🎨 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        run_command("cd frontend && npm install", "Installing npm dependencies")
    
    return True

def handle_port_conflict():
    """Handle port conflicts by trying alternative ports"""
    print("\n🔧 Handling port conflict...")
    
    # Try different ports
    for port in [8001, 8002, 8003, 8004, 8005]:
        print(f"🔄 Trying port {port}...")
        
        # Create override file for this port
        override_content = f"""# Auto-generated override for port {port}
services:
  backend:
    ports:
      - "{port}:8000"
"""
        
        with open("docker-compose.override.yml", "w") as f:
            f.write(override_content)
        
        # Try to start services
        result = run_command("docker-compose up -d", "Starting Docker services with alternative port", check=False)
        if result.returncode == 0:
            print(f"✅ Successfully started with port {port}")
            return port
    
    print("❌ Could not find an available port")
    return None

def main():
    """Main startup function"""
    print("🚀 Starting Re-Style Application...")
    print("=" * 50)
    
    # Check prerequisites
    if not check_docker():
        print("❌ Docker is required but not available. Please install Docker Desktop.")
        sys.exit(1)
    
    if not check_docker_compose():
        print("❌ Docker Compose is required but not available. Please install Docker Compose.")
        sys.exit(1)
    
    # Stop any existing containers
    print("\n🛑 Stopping any existing containers...")
    run_command("docker-compose down", "Stopping existing containers", check=False)
    
    # Remove any existing override file
    override_file = Path("docker-compose.override.yml")
    if override_file.exists():
        override_file.unlink()
        print("🧹 Removed existing docker-compose.override.yml")
    
    # Build and start Docker services
    print("\n🐳 Building and starting Docker services...")
    build_result = run_command("docker-compose build", "Building Docker images", check=False)
    if build_result.returncode != 0:
        print("❌ Docker build failed")
        sys.exit(1)
    
    # Try to start with default port first
    up_result = run_command("docker-compose up -d", "Starting Docker services", check=False)
    backend_port = 8000
    
    if up_result.returncode != 0:
        print("⚠️ Failed to start with default port, trying alternative ports...")
        backend_port = handle_port_conflict()
        if backend_port is None:
            print("❌ Could not start Docker services")
            print("💡 This might be due to port conflicts or Docker not running")
            print("💡 Try running: docker-compose down && docker-compose up -d")
            sys.exit(1)
    else:
        print("✅ Started with default port 8000")
    
    # Wait for services to be ready
    print("\n⏳ Waiting for services to start...")
    time.sleep(15)
    
    # Check if services are running
    print("\n🔍 Checking service status...")
    run_command("docker-compose ps", "Checking service status")
    
    # Wait for backend to be ready
    backend_url = f"http://localhost:{backend_port}/api/core/health/"
    if not wait_for_service(backend_url, "Backend API"):
        print("❌ Backend failed to start")
        print("💡 Check logs with: docker-compose logs backend")
        sys.exit(1)
    
    # Run database migrations
    print("\n🗄️ Setting up database...")
    run_command("docker-compose exec -T backend python manage.py migrate", "Running database migrations")
    
    # Create superuser if it doesn't exist
    print("\n👤 Checking for admin user...")
    result = run_command(
        "docker-compose exec -T backend python manage.py shell -c \"from django.contrib.auth.models import User; print('Admin exists' if User.objects.filter(username='admin').exists() else 'No admin')\"",
        "Checking admin user",
        check=False
    )
    
    if "No admin" in result.stdout:
        print("👤 Creating admin user...")
        run_command(
            "docker-compose exec -T backend python manage.py shell -c \"from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')\"",
            "Creating admin user",
            check=False
        )
    
    # Create test user if it doesn't exist
    print("\n👤 Checking for test user...")
    result = run_command(
        "docker-compose exec -T backend python manage.py shell -c \"from django.contrib.auth.models import User; print('Test user exists' if User.objects.filter(username='testuser').exists() else 'No test user')\"",
        "Checking test user",
        check=False
    )
    
    if "No test user" in result.stdout:
        print("👤 Creating test user...")
        run_command(
            "docker-compose exec -T backend python manage.py shell -c \"from django.contrib.auth.models import User; User.objects.create_user('testuser', 'test@example.com', 'testpass123')\"",
            "Creating test user",
            check=False
        )
    
    # Setup frontend
    if setup_frontend():
        print("\n🎨 Starting frontend development server...")
        print("📝 Note: Frontend will start in a new terminal window")
        print("📝 You can also start it manually with: cd frontend && npm start")
        
        # Try to start frontend in background
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen("cd frontend && npm start", shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # Unix/Linux/Mac
                subprocess.Popen("cd frontend && npm start", shell=True)
            print("✅ Frontend started in background")
        except Exception as e:
            print(f"⚠️ Could not start frontend automatically: {e}")
            print("📝 Please start frontend manually: cd frontend && npm start")
    
    # Final status check
    print("\n🔍 Final service status:")
    run_command("docker-compose ps", "Service status")
    
    print("\n" + "=" * 50)
    print("🎉 Re-Style Application is starting up!")
    print("\n📋 Access URLs:")
    print(f"   Backend API: http://localhost:{backend_port}/")
    print("   Frontend: http://localhost:3000/")
    print(f"   Admin Panel: http://localhost:{backend_port}/admin/")
    print("\n👤 Default Users:")
    print("   Admin: admin / admin123")
    print("   Test User: testuser / testpass123")
    print("\n📝 Useful Commands:")
    print("   View logs: docker-compose logs -f")
    print("   Stop services: docker-compose down")
    print("   Restart services: docker-compose restart")
    print("\n🔧 Troubleshooting:")
    print("   If frontend doesn't start: cd frontend && npm install && npm start")
    print("   If backend has issues: docker-compose logs backend")
    print("   If Celery has issues: docker-compose logs celery_worker")
    print("   If port conflicts: docker-compose down && python start_restyle_fixed.py")
    print("=" * 50)

if __name__ == "__main__":
    main() 