#!/usr/bin/env python3
"""
Setup script for local development environment.
Run this after cloning the repository to set up the development environment.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def main():
    """Main setup function."""
    print("🚀 Setting up Re-Style Django Backend for development...")
    
    # Check if we're in the right directory
    if not os.path.exists('backend/manage.py'):
        print("❌ Please run this script from the root of the restyle_project repository")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create .env from template if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('env.template'):
            print("📝 Creating .env file from template...")
            with open('env.template', 'r') as template:
                content = template.read()
            
            # Generate a random SECRET_KEY for development
            try:
                from django.core.management.utils import get_random_secret_key
                secret_key = get_random_secret_key()
                content = content.replace('your-secret-key-here', secret_key)
                content = content.replace('DEBUG=false', 'DEBUG=true')
                content = content.replace('DJANGO_SETTINGS_MODULE=backend.settings.prod', 'DJANGO_SETTINGS_MODULE=backend.settings.dev')
            except ImportError:
                print("⚠️  Django not installed yet, will set basic .env")
            
            with open('.env', 'w') as env_file:
                env_file.write(content)
            
            print("✅ .env file created from template")
        else:
            print("⚠️  No env.template found, creating basic .env")
            with open('.env', 'w') as env_file:
                env_file.write("DEBUG=true\nDJANGO_SETTINGS_MODULE=backend.settings.dev\n")
    else:
        print("✅ .env file already exists")
    
    # Install requirements
    print("\n📦 Installing Python dependencies...")
    
    # Try to install core dependencies first
    core_deps = [
        "Django==4.2.13",
        "djangorestframework==3.15.1", 
        "django-cors-headers==4.3.1",
        "gunicorn==23.0.0",
        "dj-database-url",
        "whitenoise==6.7.0"
    ]
    
    for dep in core_deps:
        result = run_command(f"pip install {dep}", f"Installing {dep}")
        if not result:
            print(f"⚠️  Failed to install {dep}, continuing...")
    
    # Change to backend directory
    os.chdir('backend')
    
    # Run migrations
    run_command("python manage.py migrate", "Running database migrations")
    
    # Create superuser
    run_command("python manage.py create_prod_superuser", "Creating admin user")
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. cd backend")
    print("2. python manage.py runserver")
    print("3. Visit http://localhost:8000/health/ to verify the setup")
    print("4. Visit http://localhost:8000/admin/ to access admin (user: elliotttmiller, password: elliott)")
    print("\n📚 For more information, see the README.md file")

if __name__ == "__main__":
    main()