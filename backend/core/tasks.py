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