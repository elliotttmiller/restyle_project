#!/usr/bin/env python3
"""
Test script to verify Django startup and health check endpoints
"""
import os
import sys
import django
import requests
import time
import subprocess
import signal
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

def test_django_startup():
    """Test if Django can start without errors"""
    print("Testing Django startup...")
    
    try:
        django.setup()
        print("✓ Django setup successful")
        
        # Test URL configuration
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test root endpoint
        response = client.get('/')
        print(f"✓ Root endpoint status: {response.status_code}")
        print(f"  Response: {response.content.decode()}")
        
        # Test health endpoint
        response = client.get('/health/')
        print(f"✓ Health endpoint status: {response.status_code}")
        print(f"  Response: {response.content.decode()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Django startup failed: {e}")
        return False

def test_gunicorn_startup():
    """Test if Gunicorn can start the Django app"""
    print("\nTesting Gunicorn startup...")
    
    try:
        # Start Gunicorn in background
        process = subprocess.Popen([
            'gunicorn', 
            'backend.wsgi:application',
            '--bind', '0.0.0.0:8001',  # Use different port
            '--workers', '1',
            '--timeout', '30',
            '--log-level', 'info'
        ], cwd=str(backend_path))
        
        # Wait for startup
        time.sleep(5)
        
        # Test endpoints
        try:
            response = requests.get('http://localhost:8001/', timeout=10)
            print(f"✓ Root endpoint via Gunicorn: {response.status_code}")
            print(f"  Response: {response.json()}")
            
            response = requests.get('http://localhost:8001/health/', timeout=10)
            print(f"✓ Health endpoint via Gunicorn: {response.status_code}")
            print(f"  Response: {response.json()}")
            
            success = True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")
            success = False
        
        # Cleanup
        process.terminate()
        process.wait()
        
        return success
        
    except Exception as e:
        print(f"✗ Gunicorn startup failed: {e}")
        return False

def test_railway_script():
    """Test the Railway startup script"""
    print("\nTesting Railway startup script...")
    
    script_path = backend_path / 'railway_start.sh'
    
    if not script_path.exists():
        print(f"✗ Railway script not found: {script_path}")
        return False
    
    print(f"✓ Railway script exists: {script_path}")
    
    # Check script permissions
    try:
        result = subprocess.run(['bash', '-n', str(script_path)], 
                              capture_output=True, text=True, cwd=str(backend_path))
        if result.returncode == 0:
            print("✓ Railway script syntax is valid")
        else:
            print(f"✗ Railway script syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Could not check script syntax: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("=== Railway Deployment Test ===\n")
    
    tests = [
        test_django_startup,
        test_gunicorn_startup,
        test_railway_script
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ All tests passed! Railway deployment should work.")
    else:
        print("✗ Some tests failed. Check the issues above.")
        sys.exit(1) 