#!/usr/bin/env python3
"""
Test script to verify Railway endpoints
"""
import requests
import time
import sys


def test_endpoint(base_url, endpoint, description):
    """Test a specific endpoint."""
    import logging
    logger = logging.getLogger(__name__)
    url = f"{base_url}{endpoint}"
    try:
        logger.info(f"Testing {description}...")
        response = requests.get(url, timeout=30)
        logger.info(f"{description}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Response: {data}")
        else:
            logger.error(f"Error: {response.text}")
        assert response.status_code == 200, f"{description} failed: {response.text}"
    except requests.exceptions.RequestException as e:
        logger.error(f"{description}: Error - {e}")
        raise


def main():
    """Test all endpoints."""
    import logging
    logger = logging.getLogger(__name__)
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://restyleproject-production.up.railway.app"
    logger.info(f"Testing Railway endpoints at: {base_url}")
    logger.info("=" * 50)
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check (no trailing slash)"),
        ("/health/", "Health check (with trailing slash)"),
        ("/test/", "Test endpoint"),
    ]
    all_passed = True
    for endpoint, description in endpoints:
        try:
            test_endpoint(base_url, endpoint, description)
        except AssertionError as e:
            logger.error(e)
            all_passed = False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            all_passed = False
    if all_passed:
        logger.info("All endpoints are working!")
    else:
        logger.error("Some endpoints failed")
        sys.exit(1)

if __name__ == '__main__':
    main()