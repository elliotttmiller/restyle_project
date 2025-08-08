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
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Add backend to Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

def test_django_startup():
    """Test if Django can start without errors."""
    try:
        django.setup()
        logger.info("Django setup successful")
        from django.urls import reverse
        from django.test import Client
        client = Client()
        # Test root endpoint
        response = client.get('/')
        logger.info(f"Root endpoint status: {response.status_code}")
        logger.debug(f"Root response: {response.content.decode()}")
        assert response.status_code in [200, 404], f"Root endpoint failed: {response.content.decode()}"
        # Test health endpoint
        response = client.get('/health/')
        logger.info(f"Health endpoint status: {response.status_code}")
        logger.debug(f"Health response: {response.content.decode()}")
        assert response.status_code == 200, f"Health endpoint failed: {response.content.decode()}"
    except Exception as e:
        logger.error(f"Django startup failed: {e}")
        raise

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
        import logging
        logger = logging.getLogger(__name__)
        # Test endpoints
        try:
            response = requests.get('http://localhost:8001/', timeout=10)
            logger.info(f"Root endpoint via Gunicorn: {response.status_code}")
            logger.debug(f"Root response: {response.json()}")
            response = requests.get('http://localhost:8001/health/', timeout=10)
            logger.info(f"Health endpoint via Gunicorn: {response.status_code}")
            logger.debug(f"Health response: {response.json()}")
            success = True
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            success = False
        # Cleanup
        process.terminate()
        process.wait()
        return success
    except Exception as e:
        logger.error(f"Gunicorn startup failed: {e}")
        return False


def test_railway_script():
    """Test the Railway startup script."""
    import logging
    logger = logging.getLogger(__name__)
    script_path = backend_path / 'railway_start.sh'
    if not script_path.exists():
        logger.error(f"Railway script not found: {script_path}")
        return False
    logger.info(f"Railway script exists: {script_path}")
    # Check script permissions
    try:
        result = subprocess.run(['bash', '-n', str(script_path)], 
                              capture_output=True, text=True, cwd=str(backend_path))
        if result.returncode == 0:
            logger.info("Railway script syntax is valid")
        else:
            logger.error(f"Railway script syntax error: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Could not check script syntax: {e}")
        return False
    return True


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("=== Railway Deployment Test ===\n")
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
            logger.error(f"Test failed with exception: {e}")
            results.append(False)
    logger.info(f"\n=== Test Results ===")
    logger.info(f"Passed: {sum(results)}/{len(results)}")
    if all(results):
        logger.info("All tests passed! Railway deployment should work.")
    else:
        logger.error("Some tests failed. Check the issues above.")
        sys.exit(1)