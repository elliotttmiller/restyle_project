# File: backend/core/tasks.py

import requests
import base64
import json
from decimal import Decimal
from celery import shared_task, group
from django.conf import settings
from django.db.models import Avg, Min, Max, Count
from .models import Item, MarketAnalysis, ComparableSale, Listing
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError as EbayConnectionError
import logging
from datetime import datetime, timedelta
import time
import os
import numpy as np
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

def get_ebay_oauth_token():
    """Get eBay OAuth token for API access with automatic refresh"""
    try:
        from .ebay_auth import get_ebay_oauth_token as get_token
        return get_token()
    except Exception as e:
        logger.error(f"Error getting eBay OAuth token: {e}")
        # Fallback to settings token
        return getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None)

def check_ebay_rate_limits():
    """
    Check eBay API rate limits using the getRateLimits method.
    Returns rate limit information for all APIs.
    """
    try:
        # Check if we should use sandbox or production
        use_sandbox = getattr(settings, 'EBAY_SANDBOX', False)
        
        # Use appropriate App ID based on environment
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
        
        logger.info(f"Checking eBay rate limits (sandbox: {use_sandbox})")
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
    """
    Check if we should skip API calls due to rate limits.
    Returns True if we should skip, False if we can proceed.
    """
    rate_limit_data = check_ebay_rate_limits()
    
    if not rate_limit_data:
        # If we can't check rate limits, proceed with caution
        logger.warning("Could not check rate limits, proceeding with API call")
        return False
    
    try:
        # Look for FindingService rate limits
        rate_limits = rate_limit_data.get('getRateLimitsResponse', [{}])[0].get('rateLimits', [])
        
        for api_limit in rate_limits:
            api_name = api_limit.get('apiName', '')
            if api_name == 'browse':  # FindingService API
                resources = api_limit.get('resources', [])
                
                for resource in resources:
                    resource_name = resource.get('name', '')
                    if resource_name == 'findCompletedItems':
                        rates = resource.get('rates', [])
                        
                        for rate in rates:
                            remaining = rate.get('remaining', 0)
                            limit = rate.get('limit', 0)
                            reset_time = rate.get('reset', '')
                            time_window = rate.get('timeWindow', 0)
                            
                            logger.info(f"Rate limit info - Remaining: {remaining}/{limit}, Reset: {reset_time}, Window: {time_window}s")
                            
                            # If we have very few calls remaining, skip this call
                            if remaining <= 2:
                                logger.warning(f"Rate limit nearly exhausted ({remaining} calls remaining), skipping API call")
                                return True
                            
                            # If we have reasonable calls remaining, proceed
                            if remaining > 5:
                                logger.info(f"Rate limit healthy ({remaining} calls remaining), proceeding with API call")
                                return False
                            
                            # For borderline cases, add a delay
                            logger.info(f"Rate limit moderate ({remaining} calls remaining), adding delay")
                            time.sleep(5)  # Add 5 second delay
                            return False
        
        # If we can't find specific rate limit info, proceed with caution
        logger.warning("Could not find specific rate limit info, proceeding with caution")
        return False
        
    except Exception as e:
        logger.error(f"Error parsing rate limit data: {e}")
        return False

@shared_task
def aggregate_analysis_results(results, analysis_id):
    """Aggregate results from multiple API calls"""
    try:
        analysis = MarketAnalysis.objects.get(id=analysis_id)
        comps = ComparableSale.objects.filter(analysis=analysis)
        rate_limited = any(result.get('rate_limited', False) for result in results)
        prices = [float(comp.sold_price) for comp in comps]
        outliers_removed = 0
        filtered_prices = prices
        if len(prices) >= 3:
            q1 = np.percentile(prices, 25)
            q3 = np.percentile(prices, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            filtered_prices = [p for p in prices if lower_bound <= p <= upper_bound]
            outliers_removed = len(prices) - len(filtered_prices)
        if filtered_prices:
            median_price = float(np.median(filtered_prices))
            min_price = min(filtered_prices)
            max_price = max(filtered_prices)
        else:
            median_price = min_price = max_price = 0
        analysis.suggested_price = Decimal(str(round(median_price, 2)))
        analysis.price_range_low = Decimal(str(round(min_price, 2)))
        analysis.price_range_high = Decimal(str(round(max_price, 2)))
        # Confidence score based on number of comps after filtering
        if len(filtered_prices) >= 10:
            analysis.confidence_score = "HIGH"
        elif len(filtered_prices) >= 5:
            analysis.confidence_score = "MEDIUM"
        elif len(filtered_prices) > 0:
            analysis.confidence_score = "LOW"
        else:
            if rate_limited:
                analysis.suggested_price = Decimal('75.00')
                analysis.price_range_low = Decimal('60.00')
                analysis.price_range_high = Decimal('90.00')
                analysis.confidence_score = "LOW (Rate Limited)"
            else:
                analysis.suggested_price = Decimal('50.00')
                analysis.price_range_low = Decimal('40.00')
                analysis.price_range_high = Decimal('60.00')
                analysis.confidence_score = "LOW"
        analysis.status = "COMPLETED"
        analysis.save()
        logger.info(f"[ANALYSIS] IQR filtering: {outliers_removed} outliers removed, {len(filtered_prices)} comps used.")
        return {"status": "success", "analysis_id": analysis_id, "rate_limited": rate_limited, "outliers_removed": outliers_removed}
    except MarketAnalysis.DoesNotExist:
        return {"status": "error", "message": "Analysis not found"}
    except Exception as e:
        logger.error(f"Error in aggregate_analysis_results: {e}")
        return {"status": "error", "message": str(e)}

@shared_task(name="core.tasks.perform_market_analysis")
def perform_market_analysis(analysis_id):
    print(f"[DEBUG] perform_market_analysis called for analysis_id={analysis_id}")
    logger.info(f"[DEBUG] perform_market_analysis called for analysis_id={analysis_id}")
    try:
        analysis = MarketAnalysis.objects.get(id=analysis_id)
        analysis.status = "IN_PROGRESS"
        analysis.save()
        # Use RESTful Browse API
        browse_result = call_ebay_browse_api_restful(analysis_id)
        if browse_result["status"] == "success":
            aggregate_result = aggregate_analysis_results([browse_result], analysis_id)
            return aggregate_result
        else:
            analysis.status = "FAILED"
            analysis.save()
            return browse_result
    except MarketAnalysis.DoesNotExist:
        return {"status": "error", "message": "Analysis not found"}
    except Exception as e:
        logger.error(f"Error in perform_market_analysis: {e}")
        return {"status": "error", "message": str(e)}

def call_ebay_browse_api_restful(analysis_id):
    """
    Call eBay RESTful Browse API to get items for market analysis.
    """
    logger.info(f"[ANALYSIS] Starting eBay Browse API call for analysis {analysis_id}")
    try:
        analysis = MarketAnalysis.objects.get(id=analysis_id)
        item = analysis.item
        oauth_token = getattr(settings, 'EBAY_PRODUCTION_USER_TOKEN', None)
        logger.info(f"[DEBUG] Using OAuth token: {str(oauth_token)[:10]}... (length: {len(str(oauth_token)) if oauth_token else 0})")
        if not oauth_token:
            logger.warning(f"No OAuth2 token available for analysis {analysis_id}, returning no data")
            return {"status": "success", "analysis_id": analysis_id, "items_found": 0, "no_token": True}
        
        # Use eBay category ID if available, otherwise fallback
        category_id = item.ebay_category_id or '11450'
        # Use only title if brand is 'Unknown' or empty
        if not item.brand or item.brand.strip().lower() == 'unknown':
            search_query = item.title
        else:
            search_query = f"{item.brand} {item.title}"
        params = {
            "q": search_query,
            "category_ids": category_id,
            "limit": 10
        }
        headers = {
            "Authorization": f"Bearer {oauth_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        api_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        logger.info(f"Calling eBay Browse API (RESTful) for analysis {analysis_id}")
        logger.info(f"[ANALYSIS] eBay Browse API params: {params}")
        logger.info(f"[ANALYSIS] eBay Browse API headers: {headers}")
        
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=15)
            logger.info(f"[ANALYSIS] eBay Browse API Response Status: {response.status_code}")
            logger.info(f"[ANALYSIS] eBay Browse API Response Body: {response.text}")
        except Exception as e:
            logger.error(f"[ANALYSIS] Exception during eBay API request: {e}")
            raise
        if response.status_code == 200:
            data = response.json()
            items = data.get('itemSummaries', [])
            items_found = 0
            for ebay_item in items:
                try:
                    sold_price = Decimal(str(ebay_item.get('price', {}).get('value', '0')))
                    title = ebay_item.get('title', '')
                    url = ebay_item.get('itemWebUrl', '')
                    image_url = ebay_item.get('image', {}).get('imageUrl', '')
                    logger.info(f"[REAL DATA] Parsed item: title={title}, url={url}, image_url={image_url}, price={sold_price}")
                    ComparableSale.objects.create(
                        analysis=analysis,
                        title=title,
                        sold_price=sold_price,
                        sale_date=datetime.now(),
                        platform='EBAY',
                        source_url=url,
                        image_url=image_url
                    )
                    items_found += 1
                except Exception as e:
                    logger.warning(f"Error processing eBay RESTful item: {e}")
                    continue
            logger.info(f"[ANALYSIS] [RESTFUL] Found {items_found} comparable items for analysis {analysis_id}")
            logger.info(f"[ANALYSIS] Total ComparableSale objects for analysis {analysis_id}: {ComparableSale.objects.filter(analysis=analysis).count()}")
            logger.info(f"[ANALYSIS] Finished eBay Browse API call for analysis {analysis_id}")
            return {"status": "success", "analysis_id": analysis_id, "items_found": items_found, "restful": True}
        else:
            logger.warning(f"eBay Browse API error: {response.status_code} - {response.text}")
            logger.info(f"[ANALYSIS] No comparable items created due to API error for analysis {analysis_id}")
            logger.info(f"[ANALYSIS] Finished eBay Browse API call for analysis {analysis_id}")
            return {"status": "success", "analysis_id": analysis_id, "items_found": 0, "api_error": True, "restful": True}
    except MarketAnalysis.DoesNotExist:
        logger.error(f"[ANALYSIS] MarketAnalysis with id {analysis_id} does not exist.")
        return {"status": "error", "message": "Analysis not found"}
    except Exception as e:
        logger.error(f"Error in call_ebay_browse_api_restful: {e}")
        return {"status": "success", "analysis_id": analysis_id, "items_found": 0, "error": True}

@shared_task
def create_ebay_listing(listing_id):
    """Create eBay listing for an item - DISABLED TO AVOID RATE LIMITS"""
    try:
        listing = Listing.objects.get(id=listing_id)
        item = listing.item
        
        # DISABLED: eBay listing creation to avoid rate limits
        logger.warning(f"eBay listing creation disabled for item {item.id} to avoid rate limits")
        
        # Return mock success response
        mock_ebay_item_id = f"MOCK_{listing.id}_{int(time.time())}"
        
        # Update listing with mock eBay data
        listing.is_active = True
        listing.platform_item_id = mock_ebay_item_id
        listing.listing_url = f"https://www.ebay.com/itm/{mock_ebay_item_id}"
        listing.save()
        
        logger.info(f"Created mock eBay listing {mock_ebay_item_id} for item {item.id} (API disabled)")
        return {"status": "success", "listing_id": listing_id, "ebay_item_id": mock_ebay_item_id, "mock_data": True, "api_disabled": True}
        
        # COMMENTED OUT: Original eBay API listing creation
        # # Get eBay OAuth token
        # user_token = get_ebay_oauth_token()
        # if not user_token:
        #     raise Exception("No eBay user token available")
        # 
        # # Create eBay Trading API connection
        # api = Trading(
        #     appid=getattr(settings, 'EBAY_PRODUCTION_APP_ID', ''),
        #     devid=getattr(settings, 'EBAY_PRODUCTION_DEV_ID', ''),
        #     certid=getattr(settings, 'EBAY_PRODUCTION_CERT_ID', ''),
        #     token=user_token,
        #     sandbox=False,  # Use production
        #     config_file=None  # Don't use YAML config file
        # )
        # 
        # # Prepare item data for eBay
        # item_data = {
        #     'Item': {
        #         'Title': f"{item.brand} {item.title}",
        #         'Description': f"Brand: {item.brand}\nCategory: {item.category}\nSize: {item.size}\nColor: {item.color}\nCondition: {item.get_condition_display()}",
        #         'PrimaryCategory': {'CategoryID': '11450'},  # Clothing, Shoes & Accessories
        #         'StartPrice': str(listing.list_price),
        #         'Currency': 'USD',
        #         'Country': 'US',
        #         'Location': 'US',
        #         'ListingDuration': 'Days_7',
        #         'PaymentMethods': ['PayPal'],
        #         'PayPalEmailAddress': 'your-paypal@email.com',  # Update with actual PayPal email
        #         'ReturnPolicy': {
        #             'ReturnsAcceptedOption': 'ReturnsAccepted',
        #             'RefundOption': 'MoneyBack',
        #             'ReturnsWithinOption': 'Days_30',
        #             'ShippingCostPaidByOption': 'Buyer'
        #         },
        #         'ShippingDetails': {
        #             'ShippingType': 'Flat',
        #             'ShippingServiceOptions': {
        #                 'ShippingServicePriority': '1',
        #                 'ShippingService': 'USPSFirstClass',
        #                 'ShippingServiceCost': '5.00'
        #             }
        #         },
        #         'DispatchTimeMax': '3'
        #     }
        # }
        # 
        # # Add item specifics
        # item_data['Item']['ItemSpecifics'] = {
        #     'NameValueList': [
        #         {'Name': 'Brand', 'Value': item.brand},
        #         {'Name': 'Size', 'Value': item.size},
        #         {'Name': 'Color', 'Value': item.color},
        #         {'Name': 'Condition', 'Value': item.get_condition_display()},
        #         {'Name': 'Style', 'Value': item.category}
        #     ]
        # }
        # 
        # # Call eBay API to create listing
        # response = api.execute('AddItem', item_data)
        # 
        # if response.reply.Ack == 'Success':
        #     # Update listing with eBay data
        #     listing.is_active = True
        #     listing.platform_item_id = response.reply.ItemID
        #     listing.listing_url = f"https://www.ebay.com/itm/{response.reply.ItemID}"
        #     listing.save()
        #     
        #     logger.info(f"Successfully created eBay listing {response.reply.ItemID} for item {item.id}")
        #     return {"status": "success", "listing_id": listing_id, "ebay_item_id": response.reply.ItemID}
        # else:
        #     error_msg = f"eBay API error: {response.reply.Errors[0].LongMessage if hasattr(response.reply, 'Errors') else 'Unknown error'}"
        #     logger.error(error_msg)
        #     return {"status": "error", "message": error_msg}
            
    except Listing.DoesNotExist:
        return {"status": "error", "message": "Listing not found"}
    except EbayConnectionError as e:
        logger.error(f"eBay connection error: {e}")
        return {"status": "error", "message": f"eBay connection error: {str(e)}"}
    except Exception as e:
        logger.error(f"Error in create_ebay_listing: {e}")
        return {"status": "error", "message": str(e)}

@shared_task
def test_task():
    print("Test task executed")
    return "Test task executed"

@shared_task(bind=True, max_retries=3)
def refresh_ebay_token_task(self):
    """
    Celery task to refresh eBay OAuth token
    This can be scheduled to run periodically
    """
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
        
        # Store error metrics
        cache.set('ebay_token_last_error', str(e), timeout=86400)
        
        # Retry with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries), max_retries=3)

@shared_task(bind=True, max_retries=2)
def validate_ebay_token_task(self):
    """
    Celery task to validate current eBay OAuth token
    This can be used to monitor token health
    """
    try:
        from .ebay_auth import token_manager, validate_ebay_token
        
        token = token_manager.get_valid_token()
        if not token:
            logger.warning("⚠️ No eBay token available for validation")
            cache.set('ebay_token_validation_status', 'no_token', timeout=3600)
            return {"status": "warning", "message": "No token available"}
        
        is_valid = validate_ebay_token(token)
        if is_valid:
            logger.info("✅ eBay token validation passed")
            cache.set('ebay_token_validation_status', 'valid', timeout=3600)
            cache.set('ebay_token_last_validation', datetime.now(), timeout=86400)
            return {"status": "success", "valid": True}
        else:
            logger.warning("⚠️ eBay token validation failed")
            cache.set('ebay_token_validation_status', 'invalid', timeout=3600)
            
            # Trigger alert for invalid token
            alert_token_health.delay("invalid_token", "eBay token validation failed")
            
            return {"status": "warning", "valid": False, "message": "Token may be expired"}
            
    except Exception as e:
        logger.error(f"❌ Error in eBay token validation task: {e}")
        cache.set('ebay_token_validation_status', 'error', timeout=3600)
        
        # Retry with exponential backoff
        raise self.retry(countdown=30 * (2 ** self.request.retries), max_retries=2)

@shared_task
def monitor_ebay_token_health_task():
    """
    Comprehensive monitoring task for eBay token health
    Runs daily to provide health overview
    """
    try:
        from .ebay_auth import token_manager, validate_ebay_token
        
        logger.info("🏥 Starting eBay token health monitoring...")
        
        # Collect metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'token_available': False,
            'token_valid': False,
            'last_refresh': None,
            'last_validation': None,
            'refresh_success_count': 0,
            'refresh_failure_count': 0,
            'validation_status': 'unknown'
        }
        
        # Check token availability
        token = token_manager.get_valid_token()
        if token:
            metrics['token_available'] = True
            metrics['token_valid'] = validate_ebay_token(token)
        
        # Get cached metrics
        metrics['last_refresh'] = cache.get('ebay_token_last_refresh')
        metrics['last_validation'] = cache.get('ebay_token_last_validation')
        metrics['refresh_success_count'] = cache.get('ebay_token_refresh_success_count', 0)
        metrics['refresh_failure_count'] = cache.get('ebay_token_refresh_failure_count', 0)
        metrics['validation_status'] = cache.get('ebay_token_validation_status', 'unknown')
        
        # Store comprehensive metrics
        cache.set('ebay_token_health_metrics', metrics, timeout=86400)
        
        # Check for health issues
        health_issues = []
        
        if not metrics['token_available']:
            health_issues.append("No token available")
        
        if not metrics['token_valid']:
            health_issues.append("Token is invalid")
        
        if metrics['refresh_failure_count'] > 3:
            health_issues.append(f"Multiple refresh failures: {metrics['refresh_failure_count']}")
        
        if metrics['last_refresh']:
            time_since_refresh = datetime.now() - metrics['last_refresh']
            if time_since_refresh > timedelta(hours=24):
                health_issues.append(f"Token not refreshed in {time_since_refresh.days} days")
        
        # Send alerts if issues found
        if health_issues:
            alert_token_health.delay("health_issues", f"eBay token health issues: {', '.join(health_issues)}")
            logger.warning(f"⚠️ eBay token health issues detected: {health_issues}")
        else:
            logger.info("✅ eBay token health monitoring completed - all systems healthy")
        
        return {
            "status": "success",
            "metrics": metrics,
            "health_issues": health_issues
        }
        
    except Exception as e:
        logger.error(f"❌ Error in eBay token health monitoring: {e}")
        alert_token_health.delay("monitoring_error", f"eBay token monitoring error: {str(e)}")
        return {"status": "error", "message": str(e)}

@shared_task
def alert_token_health(alert_type: str, message: str):
    """
    Send alerts for token health issues
    """
    try:
        logger.warning(f"🚨 eBay Token Alert [{alert_type}]: {message}")
        
        # Store alert in cache for dashboard
        alerts = cache.get('ebay_token_alerts', [])
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message
        }
        alerts.append(alert)
        
        # Keep only last 10 alerts
        if len(alerts) > 10:
            alerts = alerts[-10:]
        
        cache.set('ebay_token_alerts', alerts, timeout=86400)
        
        # Send email alert if configured
        if hasattr(settings, 'EBAY_ALERT_EMAIL') and settings.EBAY_ALERT_EMAIL:
            try:
                send_mail(
                    subject=f'eBay Token Alert: {alert_type}',
                    message=f"""
eBay Token Health Alert

Type: {alert_type}
Message: {message}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please check the eBay token configuration and refresh if necessary.
                    """,
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
    """
    Clean up old token logs and metrics
    Runs weekly to prevent cache bloat
    """
    try:
        logger.info("🧹 Starting eBay token logs cleanup...")
        
        # Clean up old metrics (keep last 7 days)
        old_metrics = cache.get('ebay_token_health_metrics')
        if old_metrics:
            # Keep only recent metrics
            pass  # Cache will auto-expire
        
        # Clean up old alerts (keep last 10)
        alerts = cache.get('ebay_token_alerts', [])
        if len(alerts) > 10:
            alerts = alerts[-10:]
            cache.set('ebay_token_alerts', alerts, timeout=86400)
        
        # Reset counters monthly
        current_date = datetime.now()
        if current_date.day == 1:  # First day of month
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
    """
    Emergency token refresh task
    Can be triggered manually when immediate refresh is needed
    """
    try:
        from .ebay_auth import token_manager
        
        logger.warning("🚨 Emergency eBay token refresh triggered")
        
        # Force refresh
        token = token_manager.force_refresh()
        if token:
            logger.info("✅ Emergency token refresh successful")
            
            # Send success alert
            alert_token_health.delay("emergency_refresh_success", "Emergency token refresh completed successfully")
            
            return {"status": "success", "emergency_refresh": True}
        else:
            logger.error("❌ Emergency token refresh failed")
            
            # Send failure alert
            alert_token_health.delay("emergency_refresh_failed", "Emergency token refresh failed")
            
            return {"status": "error", "emergency_refresh": False}
            
    except Exception as e:
        logger.error(f"❌ Error in emergency token refresh: {e}")
        alert_token_health.delay("emergency_refresh_error", f"Emergency refresh error: {str(e)}")
        return {"status": "error", "message": str(e)}