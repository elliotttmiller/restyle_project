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
import time
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
                            if remaining <= 1:
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
    """
    Enhanced Advanced Pricing Algorithm with 5 major improvements:
    1. Enhanced Confidence Scoring with multiple factors
    2. Geographic & Platform Weighting
    3. Seasonal & Trend Analysis
    4. Dynamic Decay Rate based on market volatility
    5. Advanced Outlier Detection with multi-dimensional analysis
    """
    logger.info(f"--- Running Enhanced Advanced Pricing Algorithm for Analysis ID: {analysis_id} ---")
    try:
        analysis = MarketAnalysis.objects.get(id=analysis_id)
        # Fetch comprehensive data including additional fields for advanced analysis
        comps = list(ComparableSale.objects.filter(analysis=analysis).values(
            'sold_price', 'sale_date', 'platform', 'source_url', 'title', 'condition'
        ))
    except MarketAnalysis.DoesNotExist:
        return f"Cannot aggregate. Analysis {analysis_id} not found."

    if not comps or len(comps) < 5:
        analysis.status = 'NO_RESULTS'
        analysis.confidence_score = f"Very Low ({len(comps)} comps)"
        analysis.save()
        return "Not enough data for advanced analysis."

    # Extract data for analysis
    prices = [float(comp['sold_price']) for comp in comps]
    sale_dates = [comp['sale_date'] for comp in comps]
    platforms = [comp['platform'] for comp in comps]
    conditions = [comp['condition'] for comp in comps]
    titles = [comp['title'] for comp in comps]

    logger.info(f"Initial analysis with {len(comps)} comparable sales")

    # --- IMPROVEMENT 1: Enhanced Confidence Scoring ---
    confidence_factors = calculate_confidence_factors(comps, prices, sale_dates, platforms)
    overall_confidence = sum(confidence_factors.values()) / len(confidence_factors)
    
    logger.info(f"Confidence Analysis: {confidence_factors}")

    # --- IMPROVEMENT 2: Advanced Outlier Detection ---
    outlier_flags = advanced_outlier_detection(prices, conditions, titles, platforms)
    filtered_comps = [comp for i, comp in enumerate(comps) if not outlier_flags[i]]
    
    if len(filtered_comps) < 3:  # Fallback if too many outliers
        filtered_comps = comps
        logger.warning("Warning: Too many outliers detected, using all data")
    
    logger.info(f"After outlier detection: {len(filtered_comps)} comps remaining")

    # --- IMPROVEMENT 3: Dynamic Decay Rate ---
    market_volatility = calculate_market_volatility(prices, sale_dates)
    decay_rate = calculate_adaptive_decay_rate(market_volatility)
    logger.info(f"Market volatility: {market_volatility:.3f}, Decay rate: {decay_rate:.3f}")

    # --- IMPROVEMENT 4: Enhanced Temporal Weighting with Seasonal Analysis ---
    weighted_prices = []
    for comp in filtered_comps:
        price = float(comp['sold_price'])
        sale_date = comp['sale_date']
        
        # Base temporal weight
        if sale_date is None:
            time_weight = 0.7
        else:
            days_old = (datetime.now(timezone.utc) - sale_date).days
            time_weight = math.exp(-decay_rate * max(0, days_old))
        
        # Seasonal adjustment
        seasonal_multiplier = calculate_seasonal_multiplier(sale_date, comp['title'])
        
        # Platform weighting
        platform_weight = get_platform_reliability_score(comp['platform'])
        
        # Geographic weighting (simplified - could be enhanced with actual location data)
        geo_weight = 1.0  # Default, could be enhanced with location data
        
        # Combined weight
        final_weight = time_weight * seasonal_multiplier * platform_weight * geo_weight
        
        weighted_prices.append({
            'price': price,
            'weight': final_weight,
            'original_weight': time_weight,
            'seasonal_mult': seasonal_multiplier,
            'platform_weight': platform_weight
        })

    # --- IMPROVEMENT 5: Enhanced Hot Zone Analysis ---
    if not weighted_prices:
        analysis.status = 'NO_RESULTS'
        analysis.save()
        return "No valid prices after filtering."

    sorted_by_price = sorted(weighted_prices, key=lambda x: x['price'])
    total_weight = sum(p['weight'] for p in sorted_by_price)

    # Find the price at which 25% and 75% of the "sales weight" is accumulated
    cumulative_weight = 0
    hot_zone_min = sorted_by_price[0]['price']
    for p in sorted_by_price:
        cumulative_weight += p['weight']
        if cumulative_weight >= total_weight * 0.25:
            hot_zone_min = p['price']
            break

    cumulative_weight = 0
    hot_zone_max = sorted_by_price[-1]['price']
    for p in sorted_by_price:
        cumulative_weight += p['weight']
        if cumulative_weight >= total_weight * 0.75:
            hot_zone_max = p['price']
            break

    # Final weighted average calculation within hot zone
    hot_zone_prices = [p for p in weighted_prices if hot_zone_min <= p['price'] <= hot_zone_max]
    
    if not hot_zone_prices:
        hot_zone_prices = weighted_prices

    sum_of_weighted_prices = sum(p['price'] * p['weight'] for p in hot_zone_prices)
    sum_of_weights_in_hot_zone = sum(p['weight'] for p in hot_zone_prices)
    
    suggested_price = sum_of_weighted_prices / sum_of_weights_in_hot_zone if sum_of_weights_in_hot_zone > 0 else 0

    # Generate detailed confidence report
    confidence_report = generate_confidence_report(confidence_factors, overall_confidence, len(filtered_comps))

    # --- Save Enhanced Results ---
    analysis.suggested_price = Decimal(suggested_price).quantize(Decimal("0.01"))
    analysis.price_range_low = Decimal(min(p['price'] for p in weighted_prices)).quantize(Decimal("0.01"))
    analysis.price_range_high = Decimal(max(p['price'] for p in weighted_prices)).quantize(Decimal("0.01"))
    analysis.confidence_score = confidence_report
    analysis.status = 'COMPLETE'
    analysis.save()

    logger.info(f"+++ Enhanced Analysis Complete. Suggested Price: ${analysis.suggested_price} +++")
    logger.info(f"Confidence: {overall_confidence:.2f}/1.0 - {confidence_report}")
    return f"Enhanced aggregation complete for Analysis {analysis.id}."

# --- HELPER FUNCTIONS FOR ENHANCED ALGORITHM ---

def calculate_confidence_factors(comps, prices, sale_dates, platforms):
    """Calculate multi-factor confidence scoring"""
    factors = {}
    
    # Data quantity factor (0-1)
    factors['data_quantity'] = min(len(comps) / 20, 1.0)
    
    # Data recency factor
    recent_sales = sum(1 for date in sale_dates if date and (datetime.now(timezone.utc) - date).days <= 30)
    factors['data_recency'] = recent_sales / len(comps) if comps else 0
    
    # Price consistency factor
    if len(prices) > 1:
        price_std = np.std(prices)
        price_mean = np.mean(prices)
        factors['price_consistency'] = max(0, 1 - (price_std / price_mean)) if price_mean > 0 else 0
    else:
        factors['price_consistency'] = 0.5
    
    # Market volatility factor (inverse relationship)
    volatility = calculate_market_volatility(prices, sale_dates)
    factors['market_stability'] = max(0, 1 - volatility)
    
    # Platform diversity factor
    unique_platforms = len(set(platforms))
    factors['platform_diversity'] = min(unique_platforms / 3, 1.0)
    
    # Geographic diversity (simplified - could be enhanced)
    factors['geographic_diversity'] = 0.8  # Default, could be enhanced with actual location data
    
    return factors

def advanced_outlier_detection(prices, conditions, titles, platforms):
    """Multi-dimensional outlier detection"""
    outlier_flags = [False] * len(prices)
    
    # Price-based outliers (IQR method)
    if len(prices) >= 4:
        q1 = np.percentile(prices, 25)
        q3 = np.percentile(prices, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        for i, price in enumerate(prices):
            if price < lower_bound or price > upper_bound:
                outlier_flags[i] = True
    
    # Condition-based outliers (if condition data is available)
    condition_groups = {}
    for i, condition in enumerate(conditions):
        if condition:
            if condition not in condition_groups:
                condition_groups[condition] = []
            condition_groups[condition].append(prices[i])
    
    # Detect condition-specific outliers
    for condition, condition_prices in condition_groups.items():
        if len(condition_prices) >= 3:
            condition_mean = np.mean(condition_prices)
            condition_std = np.std(condition_prices)
            for i, (price, comp_condition) in enumerate(zip(prices, conditions)):
                if comp_condition == condition and abs(price - condition_mean) > 2 * condition_std:
                    outlier_flags[i] = True
    
    # Platform-based validation
    platform_groups = {}
    for i, platform in enumerate(platforms):
        if platform not in platform_groups:
            platform_groups[platform] = []
        platform_groups[platform].append(prices[i])
    
    # Detect platform-specific outliers
    for platform, platform_prices in platform_groups.items():
        if len(platform_prices) >= 3:
            platform_mean = np.mean(platform_prices)
            platform_std = np.std(platform_prices)
            for i, (price, comp_platform) in enumerate(zip(prices, platforms)):
                if comp_platform == platform and abs(price - platform_mean) > 2.5 * platform_std:
                    outlier_flags[i] = True
    
    return outlier_flags

def calculate_market_volatility(prices, sale_dates):
    """Calculate market volatility based on recent price movements"""
    if len(prices) < 2:
        return 0.5  # Default moderate volatility
    
    # Get recent prices (last 30 days if available)
    recent_prices = []
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
    
    for price, sale_date in zip(prices, sale_dates):
        if sale_date and sale_date >= cutoff_date:
            recent_prices.append(price)
    
    if len(recent_prices) < 2:
        recent_prices = prices  # Use all prices if not enough recent data
    
    # Calculate coefficient of variation
    mean_price = np.mean(recent_prices)
    std_price = np.std(recent_prices)
    
    volatility = std_price / mean_price if mean_price > 0 else 0.5
    
    return min(volatility, 1.0)  # Cap at 1.0

def calculate_adaptive_decay_rate(volatility):
    """Calculate adaptive decay rate based on market volatility - FINE-TUNED"""
    base_decay_rate = 0.03  # Reduced from 0.05 for more gradual decay

    if volatility > 0.25:  # Lowered threshold from 0.3 - more sensitive to volatility
        return base_decay_rate * 1.8  # Increased multiplier for high volatility
    elif volatility < 0.08:  # Lowered threshold from 0.1 - more sensitive to stability
        return base_decay_rate * 0.5  # Reduced multiplier for low volatility
    else:
        return base_decay_rate  # Moderate volatility

def calculate_seasonal_multiplier(sale_date, title):
    """Calculate seasonal adjustment multiplier - ENHANCED"""
    if not sale_date:
        return 1.0
    
    month = sale_date.month
    title_lower = title.lower()
    
    # Enhanced seasonal patterns with more categories
    # Winter items (coats, boots, etc.)
    if any(word in title_lower for word in ['coat', 'jacket', 'boot', 'sweater', 'hoodie', 'winter', 'snow']):
        if month in [12, 1, 2]:  # Winter months
            return 1.25  # Increased from 1.2
        elif month in [6, 7, 8]:  # Summer months
            return 0.75  # Decreased from 0.8
    
    # Summer items (shorts, t-shirts, etc.)
    elif any(word in title_lower for word in ['shorts', 't-shirt', 'tank', 'swimsuit', 'summer', 'beach']):
        if month in [6, 7, 8]:  # Summer months
            return 1.25  # Increased from 1.2
        elif month in [12, 1, 2]:  # Winter months
            return 0.75  # Decreased from 0.8
    
    # Electronics (holiday season impact)
    elif any(word in title_lower for word in ['iphone', 'samsung', 'laptop', 'computer', 'gaming', 'console']):
        if month in [11, 12]:  # Holiday season
            return 1.15  # Holiday premium
        elif month in [1, 2]:  # Post-holiday
            return 0.85  # Post-holiday discount
    
    # Sports equipment (AI-driven seasonal detection)
    # Look for patterns that suggest sports equipment without hardcoded terms
    sports_indicators = ['equipment', 'gear', 'uniform', 'jersey', 'athletic', 'sport']
    if any(indicator in title_lower for indicator in sports_indicators):
        if month in [3, 4, 5, 9, 10]:  # Sports seasons
            return 1.1
        else:
            return 0.9
    
    # Default seasonal pattern (general retail)
    if month in [11, 12]:  # Holiday season
        return 1.1
    elif month in [1, 2]:  # Post-holiday
        return 0.9
    
    return 1.0

def get_platform_reliability_score(platform):
    """Get platform reliability weighting - FINE-TUNED"""
    platform_scores = {
        'EBAY': 1.0,      # Most reliable
        'ETSY': 0.92,     # Slightly increased from 0.9
        'AMAZON': 0.97,   # Slightly increased from 0.95
        'FACEBOOK': 0.75, # Slightly decreased from 0.8
        'CRAIGSLIST': 0.65, # Slightly decreased from 0.7
        'MERCARI': 0.85,  # New platform
        'POSHMARK': 0.88, # New platform
        'DEPOP': 0.82,    # New platform
        'OTHER': 0.75     # Decreased from 0.8
    }
    
    return platform_scores.get(platform.upper(), 0.75)

def generate_confidence_report(confidence_factors, overall_confidence, comps_count):
    """Generate detailed confidence report - ENHANCED"""
    # Fine-tuned confidence thresholds
    if overall_confidence >= 0.85:  # Increased from 0.8
        level = "Very High"
    elif overall_confidence >= 0.65:  # Increased from 0.6
        level = "High"
    elif overall_confidence >= 0.45:  # Increased from 0.4
        level = "Medium"
    elif overall_confidence >= 0.25:  # Increased from 0.2
        level = "Low"
    else:
        level = "Very Low"
    
    # Enhanced recommendations
    recommendations = []
    if confidence_factors['data_quantity'] < 0.4:  # Lowered threshold
        recommendations.append("More data needed")
    if confidence_factors['data_recency'] < 0.25:  # Lowered threshold
        recommendations.append("Recent data limited")
    if confidence_factors['price_consistency'] < 0.4:  # Lowered threshold
        recommendations.append("High price variance")
    if confidence_factors['market_stability'] < 0.4:  # Lowered threshold
        recommendations.append("Market volatility detected")
    if confidence_factors['platform_diversity'] < 0.3:  # New threshold
        recommendations.append("Limited platform diversity")
    
    report = f"{level} ({comps_count} comps, {overall_confidence:.2f}/1.0)"
    if recommendations:
        report += f" - {'; '.join(recommendations)}"
    
    return report

@shared_task(name="core.tasks.perform_market_analysis")
def perform_market_analysis(analysis_id):
    logger.error(f"[PERFORM_MARKET_ANALYSIS] Called for analysis_id={analysis_id}")
    logger.debug(f"[DEBUG] perform_market_analysis called for analysis_id={analysis_id}")
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
    logger.error(f"[CALL_EBAY_BROWSE_API_RESTFUL] Called for analysis_id={analysis_id}")
    """
    Call eBay RESTful Browse API to get items for market analysis.
    """
    logger.info(f"[ANALYSIS] Starting eBay Browse API call for analysis {analysis_id}")
    try:
        analysis = MarketAnalysis.objects.get(id=analysis_id)
        item = analysis.item
        # Use the same token logic as the manual search endpoint
        try:
            from .ebay_auth import get_ebay_oauth_token
            oauth_token = get_ebay_oauth_token()
        except Exception as e:
            logger.error(f"Error getting eBay token: {e}")
            oauth_token = None
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
    """Create eBay listing for an item using eBay Trading API"""
    try:
        listing = Listing.objects.get(id=listing_id)
        item = listing.item
        
        logger.info(f"Starting eBay listing creation for item {item.id} (listing {listing_id})")
        
        # Get eBay OAuth token
        user_token = get_ebay_oauth_token()
        if not user_token:
            logger.error("No eBay user token available for listing creation")
            return {"status": "error", "message": "No eBay user token available"}
        
        # Check rate limits before proceeding
        if should_skip_api_call():
            logger.warning("Skipping eBay listing creation due to rate limits")
            return {"status": "error", "message": "eBay API rate limit reached, please try again later"}
        
        # Create eBay Trading API connection
        api = Trading(
            appid=getattr(settings, 'EBAY_PRODUCTION_APP_ID', ''),
            devid=getattr(settings, 'EBAY_PRODUCTION_DEV_ID', ''),
            certid=getattr(settings, 'EBAY_PRODUCTION_CERT_ID', ''),
            token=user_token,
            sandbox=False,  # Use production
            config_file=None  # Don't use YAML config file
        )
        
        # Prepare item data for eBay
        item_data = {
            'Item': {
                'Title': f"{item.brand} {item.title}",
                'Description': f"Brand: {item.brand}\nCategory: {item.category}\nSize: {item.size}\nColor: {item.color}\nCondition: {item.get_condition_display()}",
                'PrimaryCategory': {'CategoryID': '15709'},  # Athletic Shoes (leaf category)
                'StartPrice': str(listing.list_price),
                'Currency': 'USD',
                'Country': 'US',
                'Location': 'US',
                'ListingDuration': 'Days_7',
                'ReturnPolicy': {
                    'ReturnsAcceptedOption': 'ReturnsAccepted',
                    'RefundOption': 'MoneyBack',
                    'ReturnsWithinOption': 'Days_30',
                    'ShippingCostPaidByOption': 'Buyer'
                },
                'ShippingDetails': {
                    'ShippingType': 'Flat',
                    'ShippingServiceOptions': {
                        'ShippingServicePriority': '1',
                        'ShippingService': 'USPSFirstClass',
                        'ShippingServiceCost': '5.00'
                    }
                },
                'DispatchTimeMax': '3',
                'ConditionID': '1000'  # New with box
            }
        }
        
        # Add item specifics
        item_data['Item']['ItemSpecifics'] = {
            'NameValueList': [
                {'Name': 'Brand', 'Value': item.brand},
                {'Name': 'Size', 'Value': item.size},
                {'Name': 'Color', 'Value': item.color},
                {'Name': 'Condition', 'Value': item.get_condition_display()},
                {'Name': 'Style', 'Value': item.category},
                {'Name': 'Department', 'Value': 'Men'}  # Required for shoes category
            ]
        }
        
        # Add a placeholder image (required by eBay)
        item_data['Item']['PictureDetails'] = {
            'PictureURL': ['https://via.placeholder.com/400x400/cccccc/666666?text=No+Image+Available']
        }
        
        logger.info(f"Calling eBay API to create listing for item {item.id}")
        
        # Call eBay API to create listing
        response = api.execute('AddItem', item_data)
        
        # Check if we have an ItemID (success) even if there are warnings
        if hasattr(response.reply, 'ItemID') and response.reply.ItemID:
            ebay_item_id = response.reply.ItemID
            # --- Verification step: Call GetItem to confirm listing is active ---
            try:
                getitem_response = api.execute('GetItem', {'ItemID': ebay_item_id})
                listing_status = getattr(getitem_response.reply, 'ListingStatus', None)
                if listing_status and listing_status.upper() == 'ACTIVE':
                    listing.is_active = True
                else:
                    listing.is_active = False
                    logger.error(f"eBay listing {ebay_item_id} for item {item.id} is not active after creation. ListingStatus: {listing_status}")
            except Exception as e:
                listing.is_active = False
                logger.error(f"Failed to verify eBay listing {ebay_item_id} for item {item.id}: {e}")
            # --- End verification step ---
            listing.platform_item_id = ebay_item_id
            listing.listing_url = f"https://www.ebay.com/itm/{ebay_item_id}"
            listing.save()
            logger.info(f"Successfully created eBay listing {ebay_item_id} for item {item.id}")
            
            # Check for warnings but don't treat them as errors
            warnings = []
            if hasattr(response.reply, 'Errors'):
                for error in response.reply.Errors:
                    if error.SeverityCode == 'Warning':
                        warnings.append(error.LongMessage)
                        logger.warning(f"eBay warning: {error.LongMessage}")
            
            return {
                "status": "success", 
                "listing_id": listing_id, 
                "ebay_item_id": response.reply.ItemID,
                "warnings": warnings
            }
        else:
            error_msg = f"eBay API error: {response.reply.Errors[0].LongMessage if hasattr(response.reply, 'Errors') else 'Unknown error'}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        

            
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
    logger.info("Test task executed")
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

# --- PERFORMANCE TRACKING FOR DASHBOARD ---
# All performance tracking functions removed