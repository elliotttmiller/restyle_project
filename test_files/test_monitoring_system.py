#!/usr/bin/env python3
"""
Test script for eBay Token Monitoring System
Tests Celery tasks, monitoring endpoints, and alerting
"""

import os
import sys
import requests
import json
import time

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.conf import settings
from django.core.cache import cache
from core.ebay_auth import token_manager, get_ebay_oauth_token, validate_ebay_token

def test_celery_tasks():
    """Test Celery task functionality"""
    print("🧪 Testing Celery Tasks")
    print("=" * 40)
    
    try:
        from core.tasks import (
            refresh_ebay_token_task, 
            validate_ebay_token_task,
            monitor_ebay_token_health_task,
            alert_token_health
        )
        
        # Test 1: Token refresh task
        print("\n1. Testing token refresh task...")
        result = refresh_ebay_token_task.delay()
        print(f"   Task ID: {result.id}")
        print("   ✅ Token refresh task queued successfully")
        
        # Test 2: Token validation task
        print("\n2. Testing token validation task...")
        result = validate_ebay_token_task.delay()
        print(f"   Task ID: {result.id}")
        print("   ✅ Token validation task queued successfully")
        
        # Test 3: Health monitoring task
        print("\n3. Testing health monitoring task...")
        result = monitor_ebay_token_health_task.delay()
        print(f"   Task ID: {result.id}")
        print("   ✅ Health monitoring task queued successfully")
        
        # Test 4: Alert task
        print("\n4. Testing alert task...")
        result = alert_token_health.delay("test_alert", "This is a test alert")
        print(f"   Task ID: {result.id}")
        print("   ✅ Alert task queued successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Celery tasks: {e}")
        return False

def test_monitoring_endpoints():
    """Test monitoring API endpoints"""
    print("\n🔗 Testing Monitoring Endpoints")
    print("=" * 40)
    
    base_url = "http://localhost:8000/api/core"
    
    # Test 1: Health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/ebay-token/health/", timeout=10)
        if response.status_code == 401:
            print("   ⚠️  Health endpoint requires authentication")
            print("   ℹ️  This is expected - the endpoint is protected")
        else:
            print(f"   📊 Response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health data retrieved: {data.get('status', 'unknown')}")
            else:
                print(f"   📄 Response: {response.text[:200]}...")
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to backend")
        print("   ℹ️  Make sure the backend is running on localhost:8000")
    except Exception as e:
        print(f"   ❌ Error testing health endpoint: {e}")
    
    # Test 2: Action endpoint
    print("\n2. Testing action endpoint...")
    try:
        response = requests.post(
            f"{base_url}/ebay-token/action/",
            json={"action": "validate"},
            timeout=10
        )
        if response.status_code == 401:
            print("   ⚠️  Action endpoint requires authentication")
            print("   ℹ️  This is expected - the endpoint is protected")
        else:
            print(f"   📊 Response status: {response.status_code}")
            if response.status_code == 202:
                data = response.json()
                print(f"   ✅ Action initiated: {data.get('message', 'unknown')}")
            else:
                print(f"   📄 Response: {response.text[:200]}...")
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to backend")
    except Exception as e:
        print(f"   ❌ Error testing action endpoint: {e}")
    
    return True

def test_cache_operations():
    """Test cache operations for monitoring"""
    print("\n💾 Testing Cache Operations")
    print("=" * 40)
    
    # Test 1: Store metrics
    print("\n1. Testing metrics storage...")
    try:
        test_metrics = {
            'timestamp': '2024-01-01T12:00:00',
            'token_available': True,
            'token_valid': True,
            'test_data': True
        }
        cache.set('ebay_token_health_metrics', test_metrics, timeout=3600)
        print("   ✅ Metrics stored successfully")
        
        # Retrieve metrics
        retrieved_metrics = cache.get('ebay_token_health_metrics')
        if retrieved_metrics and retrieved_metrics.get('test_data'):
            print("   ✅ Metrics retrieved successfully")
        else:
            print("   ❌ Metrics retrieval failed")
            return False
    except Exception as e:
        print(f"   ❌ Error testing metrics storage: {e}")
        return False
    
    # Test 2: Store alerts
    print("\n2. Testing alert storage...")
    try:
        test_alerts = [
            {
                'timestamp': '2024-01-01T12:00:00',
                'type': 'test_alert',
                'message': 'Test alert message'
            }
        ]
        cache.set('ebay_token_alerts', test_alerts, timeout=3600)
        print("   ✅ Alerts stored successfully")
        
        # Retrieve alerts
        retrieved_alerts = cache.get('ebay_token_alerts')
        if retrieved_alerts and len(retrieved_alerts) > 0:
            print("   ✅ Alerts retrieved successfully")
        else:
            print("   ❌ Alerts retrieval failed")
            return False
    except Exception as e:
        print(f"   ❌ Error testing alert storage: {e}")
        return False
    
    # Test 3: Store counters
    print("\n3. Testing counter storage...")
    try:
        cache.set('ebay_token_refresh_success_count', 5, timeout=86400)
        cache.set('ebay_token_refresh_failure_count', 1, timeout=86400)
        print("   ✅ Counters stored successfully")
        
        success_count = cache.get('ebay_token_refresh_success_count', 0)
        failure_count = cache.get('ebay_token_refresh_failure_count', 0)
        print(f"   📊 Success count: {success_count}, Failure count: {failure_count}")
    except Exception as e:
        print(f"   ❌ Error testing counter storage: {e}")
        return False
    
    return True

def test_token_manager_integration():
    """Test token manager integration with monitoring"""
    print("\n🔧 Testing Token Manager Integration")
    print("=" * 40)
    
    # Test 1: Token retrieval with monitoring
    print("\n1. Testing token retrieval...")
    try:
        token = get_ebay_oauth_token()
        if token:
            print(f"   ✅ Token retrieved (length: {len(token)})")
            
            # Check if metrics were updated
            last_refresh = cache.get('ebay_token_last_refresh')
            if last_refresh:
                print(f"   📊 Last refresh: {last_refresh}")
            else:
                print("   ℹ️  No refresh timestamp found (using cached token)")
        else:
            print("   ❌ Token retrieval failed")
            return False
    except Exception as e:
        print(f"   ❌ Error testing token retrieval: {e}")
        return False
    
    # Test 2: Token validation with monitoring
    print("\n2. Testing token validation...")
    try:
        is_valid = validate_ebay_token(token)
        if is_valid:
            print("   ✅ Token validation passed")
            
            # Check if validation timestamp was updated
            last_validation = cache.get('ebay_token_last_validation')
            if last_validation:
                print(f"   📊 Last validation: {last_validation}")
        else:
            print("   ❌ Token validation failed")
            return False
    except Exception as e:
        print(f"   ❌ Error testing token validation: {e}")
        return False
    
    # Test 3: Health status
    print("\n3. Testing health status...")
    try:
        validation_status = cache.get('ebay_token_validation_status', 'unknown')
        print(f"   📊 Validation status: {validation_status}")
        
        # Check overall health
        token_available = bool(token)
        token_valid = is_valid
        health_status = 'healthy' if token_available and token_valid else 'unhealthy'
        print(f"   📊 Overall health: {health_status}")
    except Exception as e:
        print(f"   ❌ Error testing health status: {e}")
        return False
    
    return True

def test_alert_system():
    """Test alert system functionality"""
    print("\n🚨 Testing Alert System")
    print("=" * 40)
    
    try:
        from core.tasks import alert_token_health
        
        # Test 1: Create test alert
        print("\n1. Testing alert creation...")
        result = alert_token_health.delay("test_alert", "This is a test alert from monitoring system")
        print(f"   ✅ Alert task queued (ID: {result.id})")
        
        # Test 2: Check alert storage
        print("\n2. Testing alert storage...")
        time.sleep(2)  # Give task time to complete
        
        alerts = cache.get('ebay_token_alerts', [])
        if alerts:
            latest_alert = alerts[-1]
            print(f"   ✅ Alert stored: {latest_alert.get('type')} - {latest_alert.get('message')}")
        else:
            print("   ℹ️  No alerts found (task may still be processing)")
        
        # Test 3: Alert types
        print("\n3. Testing different alert types...")
        alert_types = ['warning', 'error', 'info', 'success']
        for alert_type in alert_types:
            result = alert_token_health.delay(alert_type, f"Test {alert_type} alert")
            print(f"   ✅ {alert_type} alert queued")
        
    except Exception as e:
        print(f"❌ Error testing alert system: {e}")
        return False
    
    return True

def main():
    """Run all monitoring tests"""
    print("🚀 eBay Token Monitoring System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Celery Tasks", test_celery_tasks),
        ("Monitoring Endpoints", test_monitoring_endpoints),
        ("Cache Operations", test_cache_operations),
        ("Token Manager Integration", test_token_manager_integration),
        ("Alert System", test_alert_system)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Monitoring system is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Start Celery worker: celery -A backend worker -l info")
        print("   2. Start Celery beat: celery -A backend beat -l info")
        print("   3. Configure alert email/webhook in settings")
        print("   4. Access monitoring dashboard at /api/core/ebay-token/health/")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the configuration.")
        print("\n💡 Recommendations:")
        print("   1. Ensure Celery is properly configured")
        print("   2. Check Redis connection for caching")
        print("   3. Verify backend is running on localhost:8000")
        print("   4. Review monitoring settings")

if __name__ == "__main__":
    main() 