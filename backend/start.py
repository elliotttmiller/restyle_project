#!/usr/bin/env python3
"""
Railway startup script for Django application
"""
import os
import sys
import subprocess
import time

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(f"  Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stderr:
            print(f"  Error: {e.stderr.strip()}")
        return False

def main():
    """Main startup function"""
    print("=== Starting Restyle Backend ===")
    
    # Get port from environment
    port = os.environ.get('PORT', '8000')
    print(f"Using port: {port}")
    
    # Run migrations
    if not run_command("python manage.py migrate --noinput", "Database migrations"):
        print("Failed to run migrations")
        sys.exit(1)
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Static file collection"):
        print("Failed to collect static files")
        sys.exit(1)
    
    # Start Gunicorn
    print("Starting Gunicorn server...")
    gunicorn_cmd = [
        "gunicorn",
        "backend.wsgi:application",
        "--bind", f"0.0.0.0:{port}",
        "--workers", "1",
        "--timeout", "120",
        "--keep-alive", "5",
        "--max-requests", "1000",
        "--max-requests-jitter", "100",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--log-level", "info"
    ]
    
    try:
        subprocess.run(gunicorn_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Gunicorn failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        sys.exit(0)

if __name__ == '__main__':
    main() 