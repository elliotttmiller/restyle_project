# File: backend/core/tasks.py

import requests
import json
import math
from decimal import Decimal
from celery import shared_task
from django.conf import settings
from .models import MarketAnalysis, ComparableSale, Listing
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError as EbayConnectionError
import logging
from datetime import datetime, timedelta, timezone
import numpy as np
from django.core.cache import cache
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

def get_ebay_oauth_token():
    """Get eBay OAuth token for API access with automatic refresh"""
    try:
        from .ebay_auth import get_ebay_oauth_token as get_token
        return get_token()
    except Exception as e:
        logger.error(f"Error getting eBay OAuth token: {e}")
        return getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None)

def check_ebay_rate_limits():
    """Check eBay API rate limits using the getRateLimits method"""
    try:
        use_sandbox = getattr(settings, 'EBAY_SANDBOX', False)
        if use_sandbox:
            app_id = getattr(settings, 'EBAY_SANDBOX_APP_ID', None)
            api_url = "https://svcs.sandbox.ebay.com/services/search/FindingService/v1"
        else:
            app_id = getattr(settings, 'EBAY_PRODUCTION_APP_ID', None)
            api_url = "https://svcs.ebay.com/services/search/FindingService/v1"
        
        if not app_id:
            logger.warning("No eBay App ID available for rate limit check")
            return None
            
        headers = {
            'X-EBAY-SOA-OPERATION-NAME': 'getRateLimits',
            'X-EBAY-SOA-SECURITY-APPNAME': app_id,
            'X-EBAY-SOA-RESPONSE-DATA-FORMAT': 'JSON',
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Rate limit check successful: {json.dumps(data, indent=2)}")
            return data
        else:
            logger.warning(f"Rate limit check failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error checking eBay rate limits: {e}")
        return None

def should_skip_api_call():
    """Check if we should skip API calls due to rate limits"""
    rate_limit_data = check_ebay_rate_limits()
    
    if not rate_limit_data:
        logger.warning("Could not check rate limits, proceeding with API call")
        return False
    
    try:
        rate_limits = rate_limit_data.get('getRateLimitsResponse', [{}])[0].get('rateLimits', [])
        
        for api_limit in rate_limits:
            if api_limit.get('apiName') == 'browse':
                for resource in api_limit.get('resources', []):
                    if resource.get('name') == 'findCompletedItems':
                        usage = resource.get('usage', {})
                        limit = usage.get('limit', 0)
                        used = usage.get('used', 0)
                        if used >= limit * 0.9:  # 90% threshold
                            logger.warning(f"Rate limit approaching: {used}/{limit}")
                            return True
        return False
    except Exception as e:
        logger.error(f"Error checking rate limits: {e}")
        return False

# Helper functions
def calculate_adaptive_decay_rate(volatility):
    """Calculate adaptive decay rate based on market volatility"""
    return min(max(0.05 + 0.15 * volatility, 0.01), 0.2)

def get_platform_reliability_score(platform):
    """Get platform reliability score"""
    platform_weights = {
        'EBAY': 1.0,
        'POSHMARK': 0.9,
        'GRAILED': 0.85,
        'STOCKX': 0.95,
    }
    return platform_weights.get(platform.upper(), 0.8)

def generate_confidence_report(confidence_factors, overall_confidence, comps_count):
    """Generate confidence report based on analysis factors"""
    if overall_confidence >= 0.75:
        level = "High"
    elif overall_confidence >= 0.5:
        level = "Medium"
    elif overall_confidence >= 0.25:
        level = "Low"
    else:
        level = "Very Low"

    recommendations = []
    if confidence_factors['data_quantity'] < 0.4:
        recommendations.append("More data needed")
    if confidence_factors['data_recency'] < 0.25:
        recommendations.append("Recent data limited")
    if confidence_factors['price_consistency'] < 0.4:
        recommendations.append("High price variance")
    if confidence_factors['market_stability'] < 0.4:
        recommendations.append("Market volatility detected")
    if confidence_factors['platform_diversity'] < 0.3:
        recommendations.append("Limited platform diversity")

    report = f"{level} ({comps_count} comps, {overall_confidence:.2f}/1.0)"
    if recommendations:
        report += f" - {'; '.join(recommendations)}"
    return report

def calculate_confidence_factors(comps, prices, sale_dates, platforms):
    """Calculate multi-factor confidence scoring"""
    factors = {
        'data_quantity': min(len(comps) / 20, 1.0),
        'data_recency': (
            sum(bool(date and (datetime.now(timezone.utc) - date).days <= 30) for date in sale_dates) / len(comps)
            if comps and sale_dates else 0
        )
    }

    # Price consistency factor
    if prices:
        price_std = np.std(prices)
        price_mean = np.mean(prices)
        factors['price_consistency'] = max(0, 1 - (price_std / price_mean)) if price_mean > 0 else 0
    else:
        factors['price_consistency'] = 0.5

    # Market stability factor
    volatility = calculate_market_volatility(prices, sale_dates)
    factors['market_stability'] = max(0, 1 - volatility)

    # Platform diversity factor
    unique_platforms = len(set(platforms)) if platforms else 0
    factors['platform_diversity'] = min(unique_platforms / 4, 1.0)

    return factors

def advanced_outlier_detection(prices, conditions, platforms):
    """Detect outliers using IQR and condition-based analysis"""
    outlier_flags = [False] * len(prices)

    # Price-based outliers (IQR method)
    if len(prices) >= 4:
        q1, q3 = np.percentile(prices, [25, 75])
        iqr = q3 - q1
        lower_bound, upper_bound = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        
        for i, price in enumerate(prices):
            if price < lower_bound or price > upper_bound:
                outlier_flags[i] = True

    # Condition-based outliers
    condition_groups = {}
    for i, condition in enumerate(conditions):
        if condition:
            condition_groups.setdefault(condition, []).append((i, prices[i]))

    for condition_data in condition_groups.values():
        if len(condition_data) >= 3:
            condition_prices = [price for _, price in condition_data]
            condition_mean = np.mean(condition_prices)
            condition_std = np.std(condition_prices)
            
            for i, price in condition_data:
                if abs(price - condition_mean) > 2 * condition_std:
                    outlier_flags[i] = True

    return outlier_flags

def calculate_market_volatility(prices, sale_dates):
    """Calculate market volatility based on recent price movements"""
    if len(prices) < 2:
        return 0.5

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
    recent_prices = [
        price for price, sale_date in zip(prices, sale_dates) 
        if sale_date and sale_date >= cutoff_date
    ] or prices

    mean_price = np.mean(recent_prices)
    return min(np.std(recent_prices) / mean_price, 1.0) if mean_price > 0 else 1.0

def calculate_seasonal_multiplier(sale_date, title):
    """Calculate seasonal adjustment multiplier"""
    if not sale_date:
        return 1.0

    month = sale_date.month
    title_lower = title.lower()

    seasonal_items = {
        'winter': (['coat', 'jacket', 'boot', 'sweater', 'hoodie', 'winter', 'snow'], [12, 1, 2], [6, 7, 8]),
        'summer': (['shorts', 't-shirt', 'tank', 'swimsuit', 'summer', 'beach'], [6, 7, 8], [12, 1, 2]),
        'electronics': (['iphone', 'samsung', 'laptop', 'computer', 'gaming', 'console'], [11, 12], [1, 2]),
        'sports': (['equipment', 'gear', 'uniform', 'jersey', 'athletic', 'sport'], [3, 4, 5, 9, 10], [])
    }

    for category, (words, peak_months, low_months) in seasonal_items.items():
        if any(word in title_lower for word in words):
            if month in peak_months:
                return 1.25 if category in ['winter', 'summer'] else 1.15 if category == 'electronics' else 1.1
            elif month in low_months:
                return 0.75 if category in ['winter', 'summer'] else 0.85 if category == 'electronics' else 0.9

    return 1.1 if month in [11, 12] else 0.9 if month in [1, 2] else 1.0

def call_ebay_browse_api_restful(analysis_id):
    """Call eBay RESTful Browse API to get items for market analysis"""
    logger.info(f"Starting eBay Browse API call for analysis {analysis_id}")
    try:
        analysis = MarketAnalysis.objects.get(id=analysis_id)
        
        try:
            from .ebay_auth import get_ebay_oauth_token
            oauth_token = get_ebay_oauth_token()
        except Exception as e:
            logger.error(f"Error getting eBay token: {e}")
            return {"status": "error", "message": "No OAuth2 token available"}
        
        if not oauth_token:
            logger.warning(f"No OAuth2 token available for analysis {analysis_id}")
            return {"status": "error", "message": "No OAuth2 token available"}

        # Placeholder for actual API implementation
        return {"status": "success", "analysis_id": analysis_id, "items_found": 0}
        
    except MarketAnalysis.DoesNotExist:
        logger.error(f"MarketAnalysis with id {analysis_id} does not exist")
        return {"status": "error", "message": "Analysis not found"}
    except Exception as e:
        logger.error(f"Error in call_ebay_browse_api_restful: {e}")
        return {"status": "error", "message": str(e)}

@shared_task
def test_task():
    """Simple test task for Celery verification"""
    logger.info("Test task executed")
    return "Test task executed"

@shared_task(bind=True, max_retries=3)
def refresh_ebay_token_task(self):
    """Celery task to refresh eBay OAuth token periodically"""
    try:
        from .ebay_auth import token_manager
        logger.info("🔄 Starting scheduled eBay token refresh...")
        
        token = token_manager.get_valid_token()
        if token:
            logger.info("✅ eBay token refresh completed successfully")
            
            # Store success metrics
            cache.set('ebay_token_last_refresh', datetime.now(), timeout=86400)
            cache.set('ebay_token_refresh_success_count', 
                     cache.get('ebay_token_refresh_success_count', 0) + 1, 
                     timeout=86400)
            
            return {"status": "success", "token_length": len(token)}
        else:
            logger.error("❌ eBay token refresh failed")
            
            # Store failure metrics
            cache.set('ebay_token_last_failure', datetime.now(), timeout=86400)
            cache.set('ebay_token_refresh_failure_count', 
                     cache.get('ebay_token_refresh_failure_count', 0) + 1, 
                     timeout=86400)
            
            # Retry with exponential backoff
            raise self.retry(countdown=60 * (2 ** self.request.retries), max_retries=3)
            
    except Exception as e:
        logger.error(f"❌ Error in eBay token refresh task: {e}")
        cache.set('ebay_token_last_error', str(e), timeout=86400)
        raise self.retry(countdown=30 * (2 ** self.request.retries), max_retries=2) from e

@shared_task
def monitor_ebay_token_health_task():
    """Comprehensive monitoring task for eBay token health"""
    try:
        from .ebay_auth import token_manager, validate_ebay_token

        metrics = {
            'token_available': False,
            'token_valid': False,
            'refresh_failure_count': cache.get('ebay_token_refresh_failure_count', 0),
            'last_refresh': cache.get('ebay_token_last_refresh', None),
        }

        token = token_manager.get_valid_token()
        health_issues = []
        
        if not token:
            logger.warning("⚠️ No eBay token available for validation")
            cache.set('ebay_token_validation_status', 'no_token', timeout=3600)
            health_issues.append("No token available")
        else:
            metrics['token_available'] = True
            is_valid = validate_ebay_token(token)
            
            if is_valid:
                logger.info("✅ eBay token validation passed")
                cache.set('ebay_token_validation_status', 'valid', timeout=3600)
                cache.set('ebay_token_last_validation', datetime.now(), timeout=86400)
                metrics['token_valid'] = True
            else:
                logger.warning("⚠️ eBay token validation failed")
                cache.set('ebay_token_validation_status', 'invalid', timeout=3600)
                alert_token_health.delay("invalid_token", "eBay token validation failed")
                health_issues.append("Token is invalid")

        if metrics['refresh_failure_count'] > 3:
            health_issues.append(f"Multiple refresh failures: {metrics['refresh_failure_count']}")

        if metrics['last_refresh']:
            time_since_refresh = datetime.now() - metrics['last_refresh']
            if time_since_refresh > timedelta(hours=24):
                health_issues.append(f"Token not refreshed in {time_since_refresh.days} days")

        cache.set('ebay_token_health_metrics', metrics, timeout=86400)

        if health_issues:
            alert_token_health.delay("health_issues", f"eBay token health issues: {', '.join(health_issues)}")
            logger.warning(f"⚠️ eBay token health issues detected: {health_issues}")
        else:
            logger.info("✅ eBay token health monitoring completed - all systems healthy")

        return {"status": "success", "metrics": metrics, "health_issues": health_issues}

    except Exception as e:
        logger.error(f"❌ Error in eBay token health monitoring: {e}")
        alert_token_health.delay("monitoring_error", f"eBay token monitoring error: {str(e)}")
        return {"status": "error", "message": str(e)}

@shared_task
def alert_token_health(alert_type: str, message: str):
    """Send alerts for token health issues"""
    try:
        logger.warning(f"🚨 eBay Token Alert [{alert_type}]: {message}")

        # Store alert in cache
        alerts = cache.get('ebay_token_alerts', [])
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message
        }
        alerts.append(alert)
        
        # Keep only last 10 alerts
        alerts = alerts[-10:]
        cache.set('ebay_token_alerts', alerts, timeout=86400)

        # Send email alert if configured
        if hasattr(settings, 'EBAY_ALERT_EMAIL') and settings.EBAY_ALERT_EMAIL:
            try:
                send_mail(
                    subject=f'eBay Token Alert: {alert_type}',
                    message=(
                        f"eBay Token Health Alert\n\n"
                        f"Type: {alert_type}\n"
                        f"Message: {message}\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"Please check the eBay token configuration and refresh if necessary."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EBAY_ALERT_EMAIL],
                    fail_silently=True
                )
                logger.info(f"📧 Email alert sent for {alert_type}")
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")

        return {"status": "success", "alert_sent": True}

    except Exception as e:
        logger.error(f"❌ Error sending token alert: {e}")
        return {"status": "error", "message": str(e)}

@shared_task
def cleanup_token_logs_task():
    """Clean up old token logs and metrics"""
    try:
        logger.info("🧹 Starting eBay token logs cleanup...")
        
        # Clean up old alerts (keep last 10)
        alerts = cache.get('ebay_token_alerts', [])
        if len(alerts) > 10:
            alerts = alerts[-10:]
            cache.set('ebay_token_alerts', alerts, timeout=86400)
        
        # Reset counters monthly
        if datetime.now().day == 1:
            cache.delete('ebay_token_refresh_success_count')
            cache.delete('ebay_token_refresh_failure_count')
            logger.info("📊 Reset monthly token refresh counters")
        
        logger.info("✅ eBay token logs cleanup completed")
        return {"status": "success", "cleanup_completed": True}
        
    except Exception as e:
        logger.error(f"❌ Error in token logs cleanup: {e}")
        return {"status": "error", "message": str(e)}

@shared_task
def emergency_token_refresh_task():
    """Emergency token refresh task"""
    try:
        from .ebay_auth import token_manager
        
        logger.warning("🚨 Emergency eBay token refresh triggered")
        
        token = token_manager.force_refresh()
        if token:
            alert_token_health.delay("emergency_refresh_success", "Emergency token refresh completed successfully")
            return {"status": "success", "emergency_refresh": True}
        else:
            logger.error("❌ Emergency token refresh failed")
            alert_token_health.delay("emergency_refresh_failed", "Emergency token refresh failed")
            return {"status": "error", "emergency_refresh": False}
            
    except Exception as e:
        logger.error(f"❌ Error in emergency token refresh: {e}")
        alert_token_health.delay("emergency_refresh_error", f"Emergency refresh error: {str(e)}")
        return {"status": "error", "message": str(e)}