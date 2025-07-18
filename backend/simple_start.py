#!/usr/bin/env python3
"""
Simple startup script for Railway
"""
import os
import subprocess
import sys

def main():
    port = os.environ.get('PORT', '8080')
    print(f"Starting Django on port {port}")
    
    # Run migrations
    subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=True)
    
    # Collect static files
    subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], check=True)
    
    # Start Django development server (for testing)
    print(f"Starting Django development server on 0.0.0.0:{port}")
    subprocess.run([
        sys.executable, 'manage.py', 'runserver', 
        f'0.0.0.0:{port}', '--noreload'
    ], check=True)

if __name__ == '__main__':
    main() 